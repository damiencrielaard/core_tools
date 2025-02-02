from core_tools.data.SQL.SQL_common_commands import execute_statement, execute_query
from core_tools.data.SQL.SQL_common_commands import select_elements_in_table, insert_row_in_table, update_table
from core_tools.data.SQL.queries.dataset_creation_queries import data_table_queries

import psycopg2, json
import numpy as np

class sync_mgr_queries:
    @staticmethod
    def get_sync_items_meas_table(sync_agent):
        '''
        returns:
            meaurments <list<long>> : list of uuid's who's table entries need a sync
        '''
        res = select_elements_in_table(sync_agent.conn_local, "global_measurement_overview",
            ('uuid', ), where=("table_synchronized",False), dict_cursor=False)

        uuid_entries = list(sum(res, ()))
        uuid_entries.sort()
        return uuid_entries

    @staticmethod
    def sync_table(sync_agent, uuid, to_local=False):
        '''
        syncs row in the table to the remote for the given uuid

        Args:
            sync_agent: class holding local and remote connection
            uuid (int): unique id of measurement
            to_local (bool): if True syncs from remote to local server
        '''
        if to_local:
            conn_src = sync_agent.conn_remote
            conn_dest = sync_agent.conn_local
        else:
            conn_src = sync_agent.conn_local
            conn_dest = sync_agent.conn_remote

        # check if uuid exists
        entry_exists = select_elements_in_table(conn_dest, "global_measurement_overview",
            ('uuid', ), where=("uuid",uuid), dict_cursor=False)

        source_content = select_elements_in_table(conn_src, "global_measurement_overview",
            ('*', ), where=("uuid",uuid), dict_cursor=True)[0]
        sync_mgr_queries.convert_SQL_raw_table_entry_to_python(source_content)

        del source_content['id']
        source_content['table_synchronized'] = True


        if len(entry_exists) == 0:
            print('create measurement row', uuid)
            insert_row_in_table(conn_dest, 'global_measurement_overview',
                tuple(source_content.keys()), tuple(source_content.values()))
        else:
            print('update measurement row', uuid)
            dest_content = select_elements_in_table(conn_dest, "global_measurement_overview",
                ('*', ), where=("uuid",uuid), dict_cursor=True)[0]
            sync_mgr_queries.convert_SQL_raw_table_entry_to_python(dest_content)

            del dest_content['id']

            content_to_update = dict()

            for key in dest_content.keys():
                if source_content[key] != dest_content[key]:
                    content_to_update[key] = source_content[key]

            update_table(conn_dest, 'global_measurement_overview',
                content_to_update.keys(), content_to_update.values(),
                condition=("uuid",uuid))

        if not to_local:
            update_table(sync_agent.conn_local, 'global_measurement_overview',
                    ('table_synchronized', ), (True, ),
                    condition=("uuid",uuid))

        conn_src.commit()
        conn_dest.commit()

    @staticmethod
    def get_sync_items_raw_data(sync_agent):
        '''
        returns:
            meaurments <list<long>> : list of uuid's where the data needs to be updated of.
        '''
        res = select_elements_in_table(sync_agent.conn_local, "global_measurement_overview",
            ('uuid', ), where=('data_synchronized',False), dict_cursor=False)

        uuid_entries = list(sum(res, ()))
        uuid_entries.sort()
        return uuid_entries

    @staticmethod
    def sync_raw_data(sync_agent, uuid, to_local=False):
        if to_local:
            conn_src = sync_agent.conn_remote
            conn_dest = sync_agent.conn_local
        else:
            conn_src = sync_agent.conn_local
            conn_dest = sync_agent.conn_remote

        raw_data_table_name = select_elements_in_table(conn_src,
            'global_measurement_overview', ('exp_data_location', ),
            where=("uuid",uuid), dict_cursor=False)[0][0]

#        data_table_queries.generate_table(sync_agent.conn_local, raw_data_table_name)
        sync_mgr_queries._sync_raw_data_table(conn_src, conn_dest, raw_data_table_name)
        sync_mgr_queries._sync_raw_data_lobj(conn_src, conn_dest, raw_data_table_name)

        update_table(sync_agent.conn_local, 'global_measurement_overview',
                ('data_synchronized', ), (True, ),
                condition=("uuid",uuid))
        sync_agent.conn_local.commit()


    @staticmethod
    def _sync_raw_data_table(conn_src, conn_dest, raw_data_table_name):
        n_row_src = select_elements_in_table(conn_src, raw_data_table_name,
            (psycopg2.sql.SQL('COUNT(*)'), ), dict_cursor=False)[0][0]

        table_name = execute_query(conn_dest,
            "SELECT to_regclass('{}.{}');".format('public', raw_data_table_name))[0][0]

        n_row_dest = 0
        if table_name is not None:
            n_row_dest = select_elements_in_table(conn_dest, raw_data_table_name,
                (psycopg2.sql.SQL('COUNT(*)'), ), dict_cursor=False)[0][0]

        if n_row_src != n_row_dest or table_name == None:
            print('update raw table', raw_data_table_name)
            get_rid_of_table = "DROP TABLE IF EXISTS {} ; ".format(raw_data_table_name)
            execute_statement(conn_dest, get_rid_of_table)

            data_table_queries.generate_table(conn_dest, raw_data_table_name)

            res_src = select_elements_in_table(conn_src, raw_data_table_name, ('*', ), order_by=('id', ''))

            for result in res_src:
                lobject = conn_dest.lobject(0,'w')
                del result['id']
                result['oid'] = lobject.oid
                result['write_cursor'] = 0
                result['depencies'] = json.dumps(result['depencies'])
                result['shape'] = json.dumps(result['shape'])
                insert_row_in_table(conn_dest, raw_data_table_name,
                    result.keys(), result.values())

        conn_dest.commit()

    @staticmethod
    def _sync_raw_data_lobj(conn_src, conn_dest, raw_data_table_name):
        res_src = select_elements_in_table(conn_src, raw_data_table_name,
            ('write_cursor', 'total_size', 'oid'), order_by=('id', ''))
        res_dest = select_elements_in_table(conn_dest, raw_data_table_name,
            ('write_cursor', 'total_size', 'oid'), order_by=('id', ''))

        print('update large object', raw_data_table_name)
        for i in range(len(res_src)):
            dest_cursor = res_dest[i]['write_cursor']
            src_cursor = res_src[i]['write_cursor']
            dest_oid = res_dest[i]['oid']
            src_oid = res_src[i]['oid']
            src_lobject = conn_src.lobject(src_oid,'rb')
            dest_lobject = conn_dest.lobject(dest_oid,'wb')

            while (dest_cursor != src_cursor):
                src_lobject.seek(dest_cursor*8)
                dest_lobject.seek(dest_cursor*8)
                if src_cursor*8 - dest_cursor*8 < 2_000_000:
                    mybuffer = np.frombuffer(src_lobject.read(src_cursor*8-dest_cursor*8))
                    dest_cursor = src_cursor
                else:
                    print(f'large dataset, {(src_cursor*8-dest_cursor*8)*1e-9}GB')
                    mybuffer = np.frombuffer(src_lobject.read(2_000_000))
                    dest_cursor += int(2_000_000/8)
                dest_lobject.write(mybuffer.tobytes())

            dest_lobject.close()
            src_lobject.close()

            update_table(conn_dest, raw_data_table_name,
                ('write_cursor',), (src_cursor,), condition=('oid',dest_oid))

        conn_dest.commit()

    @staticmethod
    def convert_SQL_raw_table_entry_to_python(content):
        content['keywords'] = psycopg2.extras.Json(content['keywords'])
        content['start_time'] = psycopg2.sql.SQL("TO_TIMESTAMP({})").format(psycopg2.sql.Literal(content['start_time'].timestamp()))

        if content['snapshot'] is not None:
            content['snapshot'] = str(content['snapshot'].tobytes()).replace('\\\'', '').replace('\\\\\"', '')
            if content['snapshot'].startswith('b'):
                content['snapshot'] = content['snapshot'][1:]
            if content['snapshot'].startswith('\''):
                content['snapshot'] = content['snapshot'][1:-1]
            content['snapshot'] = psycopg2.extras.Json(json.loads(content['snapshot']))
        if content['metadata'] is not None:
            content['metadata'] = str(content['metadata'].tobytes()).replace('\\\'', '')
            if content['metadata'].startswith('b'):
                content['metadata'] = content['metadata'][1:]
            if content['metadata'].startswith('\''):
                content['metadata'] = content['metadata'][1:-1]
            content['metadata'] = psycopg2.extras.Json(json.loads(content['metadata']))

        if content['stop_time'] is not None:
            content['stop_time'] = psycopg2.sql.SQL("TO_TIMESTAMP({})").format(psycopg2.sql.Literal(content['stop_time'].timestamp()))

if __name__ == '__main__':
    from core_tools.data.SQL.connect import set_up_local_storage, set_up_remote_storage, set_up_local_and_remote_storage
    set_up_local_storage('stephan', 'magicc', 'test', 'test_project', 'test_set_up', 'test_sample')
    set_up_local_and_remote_storage('131.180.205.81', 5432, 'stephan', 'magicc', 'test',
        'stephan_test', 'magicc', 'spin_data_test', 'test_project', 'test_set_up', 'test_sample')

    set_up_local_and_remote_storage('131.180.205.81', 5432,
    "xld_user", "XLDspin001", "vandersypen_data",
    'xld_measurement_pc', 'XLDspin001', 'sixdots',
     "6dot", "XLD", "6D3S - SQ20-20-5-18-4")
    from core_tools.data.SQL.SQL_connection_mgr import SQL_sync_manager
    s = SQL_sync_manager()

    e = sync_mgr_queries.get_sync_items_meas_table(s)
    # sync_mgr_queries.sync_raw_data(s,e[11049])

    i = 0
    for uuid in e:
        print(i)
        # sync_mgr_queries.sync_raw_data(s,uuid)
        sync_mgr_queries.sync_table(s, uuid)
        i+= 1
    # # e = sync_mgr_queries.get_sync_items_raw_data(s)
    # # print(e)
    # sync_mgr_queries.sync_raw_data(s, e[-1])