from qcodes import MultiParameter
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import lmfit


def lin_func(x, a, b):
    return x*a + b


#TODO move to better location at later point
def get_phase_compentation_IQ_signal(param):
    '''
    Args:
        param (Multiparameter) : parameter with a get method that returns an I and Q array of a signal.
    Return:
        rotation_angle (double) : angle at which to rotate the signal to project it to the I plane.
    '''
    data_in = param.get()
    
    model = lmfit.Model(lin_func)
    
    a = np.average(data_in[0])/np.average(data_in[1])
    b = 0
    param = model.make_params(a=a, b=b)
    result = model.fit(data_in[1], param, x=data_in[0])
    
    angle = np.angle(1+1j*result.best_values['a'])
    
    # print(result.best_values['a'])
    # print(angle)
    # x= np.linspace(-120, 20, 100) 
    # plt.plot(x, lin_func(x, result.best_values['a'], result.best_values['b']))
    # plt.plot(data_in[0], data_in[1])
    # new_data = data_in[0] +1j*data_in[1]
    # new_data *= np.exp(1j*(-angle))
    # plt.plot(np.real(new_data), np.imag(new_data))

    # new_data = x +1j*lin_func(x, result.best_values['a'], result.best_values['b'])
    # new_data *= np.exp(1j*(-angle))
    # plt.plot(np.real(new_data), np.imag(new_data))
    return angle

class IQ_to_scalar(MultiParameter):
    '''
    parameter that converts IQ data of the digitizer into scalar data
    NOTE : ONLY ONE IQ CHANNEL PAIR SUPPORTED ATM !!!
    '''
    def __init__(self, digitizer, phase_rotation):
        '''
        Args:
            digitizer (MultiParameter) : instrument class of the digitizer
            phase_rotation (double) : rotation in the IQ plane (will keep only I)
        '''
        self.dig = digitizer
        self.phase_rotation = phase_rotation
        self.sample_rate = digitizer.sample_rate

        names = ('RF_readout_amplitude',)
        super().__init__('IQ_to_scalar_convertor', names=names, shapes=(self.dig.shapes[0],),
                         labels=(self.dig.labels[0],), units=(self.dig.units[0],),
                         setpoints=(self.dig.setpoints[0],),
                         setpoint_names=(self.dig.setpoint_names[0],),
                         setpoint_labels=(self.dig.setpoint_labels[0],),
                         setpoint_units=(self.dig.setpoint_units[0],))

    def get_raw(self):
        data_in = self.dig.get_raw()
        data_out = (data_in[0] + 1j*data_in[1])*np.exp(1j*self.phase_rotation)

        return (data_out.real, )


class down_sampler(MultiParameter):
    '''
    Down sampler for a digitizer, given a certain bandwidth, take make blibs for example more clear.
    '''
    def __init__(self, digitizer, bandwidth, highpass = None):
        '''
        Args: 
            digitizer (MultiParameter) : instrument class of the digitizer 
            bandwidth (double) : wanted bandwidth (3db point of a butterworth filter)
            highpass (double) : if defined, sets a highpass filter at a given freq
        '''
        self.dig = digitizer
        self.bandwidth = bandwidth
        self.highpass = highpass
        self.sample_rate = digitizer.sample_rate
        self.sample_drop_rate = int(self.dig.sample_rate/bandwidth/2)

        shapes, setpoints = self.get_shape()
        super().__init__('Elzerman_state_differentiator', names=digitizer.names, shapes=shapes,
                         labels=digitizer.labels, units=digitizer.units, setpoints=setpoints,
                         setpoint_names=digitizer.setpoint_names,
                         setpoint_labels=digitizer.setpoint_labels,
                         setpoint_units=digitizer.setpoint_units)

    def get_raw(self):
        data_out = tuple()
        data_in = self.dig.get()

        for i in range(len(data_in)):
            filtered_data = np.empty(self.shapes[0])

            if filtered_data.ndim == 2:
                for j in range(len(filtered_data)):
                    filtered_data[j,:] = filter_data(data_in[i][j], self.bandwidth, self.dig.sample_rate, 'lowpass')[::self.sample_drop_rate]
                
                    if self.highpass is not None:
                        filtered_data[j,:] =  filter_data(filtered_data[j], self.highpass,  self.sample_rate/self.sample_drop_rate, 'highpass')
            else:
                filtered_data[:] = filter_data(data_in[i], self.bandwidth, self.dig.sample_rate, 'lowpass')[::self.sample_drop_rate]
                
                if self.highpass is not None:
                    filtered_data[:] =  filter_data(filtered_data[:], self.highpass, self.sample_rate/self.sample_drop_rate, 'highpass')

            data_out += (filtered_data,)

        return tuple(data_out)

    def get_shape(self):
        shapes, setpoints = tuple(), tuple()

        for i in range(len(self.dig.names)):
            setpt = self.dig.setpoints[i]
            shape = tuple()

            if len(setpt) > 1:
                setpt = (setpt[0], np.asarray(setpt[1]).flatten()[::self.sample_drop_rate], )
                shape = (len(setpt[0]), len(setpt[1]))
            else:
                setpt = (np.asarray(setpt).flatten()[::self.sample_drop_rate], )
                shape = setpt[0].shape

            shapes += (shape, )
            setpoints += (setpt, )

        return shapes, setpoints

    def update_shape(self):
        self.shapes, self.setpoints = self.get_shape()

class Elzerman_param(MultiParameter):
    """
    parameter that aims to detect blibs.
    expected that the input data is already well filtered.
    """
    def __init__(self, digitizer, threshold, blib_down):
        '''
        Args:
            digitizer (MultiParameter) :  parameter providing the data for the dip detection
            threshold (double) : threadhold for the detection
            blib_down (bool) : direction of the blib (if true, downward blib expected).
        '''
        self.dig = digitizer
        self.threshold = threshold  
        self.blib_down = blib_down

        names = tuple()
        shapes = tuple()
        labels = tuple()
        units = tuple()
        setpoints = tuple()

        for i in range(len(digitizer.names)):
            names += ("readout_signal_ch{}".format(i), )
            shapes += ((), )
            labels += ('Spin probability' ,)
            units += ('%', )
            
            setpoints += ((),)

        super().__init__('Elzerman_state_differentiaor', names=names, shapes=shapes,
                         labels=labels, units=units, setpoints=setpoints)

    
    def get_raw(self):
        # expected format from the getter <tuple<np.ndarray[ndim=2,dtype=double]>>
        data_in = self.dig.get()
        data_out = []

        for data in data_in:
            if self.blib_down == True:
                blib_pt = np.where(data<self.threshold)[0]
            else :
                blib_pt = np.where(data>self.threshold)[0]
            
            data_out.append(np.unique(blib_pt).size/data.shape[0])

        return data_out

def filter_data(data, cutoff, fs, pass_zero, order = 4):
    '''
    filter noise out of a dataset
    Args:
        data (np.ndarray) : data array to filter
        cutoff (double) : cutoff in HZ (not that this is the last 0db point and not -3db)
        fs (double) : sample rate of the signal
        pass_zero (str) : 'lowpass' or 'highpass'
    '''
    b, a = signal.butter(order, cutoff/(fs/2), pass_zero)
    return signal.filtfilt(b, a, data)


if __name__ == '__main__':
    a = np.zeros([1000])
    a[100:400] = 1

    filter_data(a, 10e3, 2e6, 'highpass')