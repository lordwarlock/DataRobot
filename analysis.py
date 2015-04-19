import re
from numpy import log10

class RestData(object):
    feat_dict = dict()
    def __init__(self,features,prediction):
        self.rest_id = int(features[0])
        self._update('id', self.rest_id)

        self.open_date = features[1]
        self._update('date', self.open_date)

        self.age = 2015 - int(features[1][-4:])
        self._update('age', self.age)

        self.city = features[2]
        self._update('city', self.city)

        self.city_group = re.sub(' ','_',features[3])
        self._update('city_group', self.city_group)

        self.rest_type = int(features[4] == 'FC')
        self._update('type', self.rest_type)

        self.p = [self.process_num(x) for x in features[5:]]
        [self._update('p'+str(i+1), self.p[i]) for i in range(37)]

        if prediction != []:
            self.prediction = float(prediction[0])
        else:
            self.prediction = 0

    def process_num(self,string):
        if '.' in string:
            return float(string)
        else:
            return string

    @classmethod
    def _update(cls,field,value):
        if field in cls.feat_dict:
            cls.feat_dict[field].add(value)
        else:
            cls.feat_dict[field] = set([value])

class DataAnalysis(object):
    def __init__(self,train_dir = '../train.csv',
                      test_dir = '../test.csv'):
        self.train_data = self.readRestData(train_dir)
        self.test_data = self.readRestData(test_dir)

    def feat_selection(self,out_dir = '../feat_select/'):
        for i in range(40):
            print i
            self.output_weka_arff_filter(self.train_data,
                                         out_dir = out_dir + str(i) + '_train.arff',
                                         filter_list = [i])
            self.output_weka_arff_filter(self.test_data,
                                         out_dir = out_dir + str(i) + '_test.arff',
                                         rel_name = 'test',
                                         filter_list = [i])
             

    def readRestData(self,file_dir):
        data = []
        with open(file_dir,'r') as f_i:
            _ = f_i.readline()
            for line in f_i:
                splitted = line[:-1].split(',')
                data.append(RestData(splitted[:42],splitted[42:]))
        return data
       
    def prediction_field_match(self,data,s1,s2):
        if s1==s2:
            return data.prediction
        else:
            return 0

    def output_matlab_csv_log(self,data_list,out_dir = '../matlab/train_log.csv'):
        with open(out_dir,'w') as f_o:
            for data in data_list:
                f_o.write(str(log10(float(data.age)))+',')
                f_o.write(str(int(data.city_group == 'Big_Cities'))+',')
                f_o.write(str(data.rest_type)+',')
                p = [str(log10(1+float(x))) for x in data.p]
                f_o.write(','.join(p)+','+ str(data.prediction) +'\n')

    def output_matlab_csv(self,data_list,out_dir = '../matlab/train.csv'):
        with open(out_dir,'w') as f_o:
            for data in data_list:
                f_o.write(str(data.age)+',')
                f_o.write(str(int(data.city_group == 'Big_Cities'))+',')
                f_o.write(str(data.rest_type)+',')
                p = [str(x) for x in data.p]
                f_o.write(','.join(p)+','+ str(data.prediction) +'\n')


    def output_weka_arff(self,data_list,out_dir = '../weka/train.arff',rel_name = 'train'):
        with open(out_dir,'w') as f_o:
            f_o.write(self._get_weka_header(rel_name))
            f_o.write(self._get_weka_body(data_list))

    def output_weka_arff_filter(self,data_list,out_dir = '../weka/train.arff',rel_name = 'train',
                         filter_list = [1]):
        with open(out_dir,'w') as f_o:
            header_list = self._get_weka_header_vector(rel_name)
            body_list = self._get_weka_body_vector(data_list)
            #filter
            _ = [header_list.pop(1-i+filter_list[i]) for i in range(len(filter_list))]
            for line in body_list:
                _ = [line.pop(x) for x in filter_list]
            #output
            f_o.write('\n'.join(header_list) + '\n')
            f_o.write('\n'.join([','.join(line) for line in body_list]))

    def _get_weka_header_vector(self,rel_name = 'train'):
        header_buffer = []
        header_buffer.append( '@RELATION ' + rel_name + '\n')
        header_buffer.append( '@ATTRIBUTE\tage\tREAL')
        header_buffer.append( '@ATTRIBUTE\tcity_group\t{Big_Cities,Other}')
        header_buffer.append( '@ATTRIBUTE\ttype\t{0,1}')
        feat_len = len(self.train_data[0].p)
        for i in range(feat_len):
            header_buffer.append( '@ATTRIBUTE\tp'+str(i+1)+'\tREAL')

        header_buffer.append( '@ATTRIBUTE\trevenue\tREAL')
        header_buffer.append( '\n@DATA')
        return header_buffer

    def _get_weka_body_vector(self,data_list):
        body_buffer = []
        for data in data_list:
            line_buffer = []
            line_buffer.append( str(log10(data.age)) )
            line_buffer.append( data.city_group)
            line_buffer.append( str(1 - data.rest_type))
            p = [str(log10(1+float(x))) for x in data.p]
            line_buffer += p
            line_buffer.append( str(data.prediction))
            body_buffer.append( line_buffer )
        return body_buffer


    def _get_weka_header(self,rel_name = 'train'):
        header_buffer = '@RELATION ' + rel_name + '\n\n'
        header_buffer += '@ATTRIBUTE\tage\tREAL\n'
        header_buffer += '@ATTRIBUTE\tcity_group\t{Big_Cities,Other}\n'
        header_buffer += '@ATTRIBUTE\ttype\t{0,1}\n'
        feat_len = len(self.train_data[0].p)
        for i in range(feat_len):
            header_buffer += '@ATTRIBUTE\tp'+str(i+1)+'\tREAL\n'

        header_buffer += '@ATTRIBUTE\trevenue\tREAL\n'
        header_buffer += '\n@DATA\n'
        return header_buffer



    def _get_weka_body(self,data_list):
        body_buffer = ''
        for data in data_list:
            body_buffer += str(log10(data.age))+','
            body_buffer += data.city_group+','
            body_buffer += str(data.rest_type)+','
            p = [str(log10(1+float(x))) for x in data.p]
            body_buffer += ','.join(p)
            body_buffer += ','+str(data.prediction)+'\n'
        return body_buffer

if __name__ == '__main__':
    da = DataAnalysis()
    da.output_weka_arff_filter(da.train_data,
                               out_dir = '../weka/train.arff',
                               filter_list = [1,2])
    da.output_weka_arff_filter(da.test_data,
                               out_dir = '../weka/test.arff',
                               rel_name = 'test',
                               filter_list = [1,2])

