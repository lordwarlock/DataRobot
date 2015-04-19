import glob
import re
"89 33 11"
class WekaSummary():

    def readResult(self,
                   in_dir = '../results/',
                   out_dir = './summary/'):
        result_list = glob.glob(in_dir+'log*')
        for result_file in result_list:
            f_name = self.get_file_name(result_file)
            print f_name
            print 'Mean absolute error',self.get_accuracy(result_file,'=== Cross-validation ===','Mean absolute error',3)
            print 'Root mean squared error',self.get_accuracy(result_file,'=== Cross-validation ===','Root mean squared error',4)
            print 'Relative absolute error',self.get_accuracy(result_file,'=== Cross-validation ===','Relative absolute error',3)
            print 'Root relative squared error',self.get_accuracy(result_file,'=== Cross-validation ===','Root relative squared error',4)

            
    def get_accuracy(self,
                     file_dir,
                     hint1 = '=== Stratified cross-validation ===\n',
                     hint2 = 'Correctly Classified Instances',
                     seq_no = 4):
        result = []
        with open(file_dir) as f_i:
            flag1 = False
            len1 = len(hint1)
            len2 = len(hint2)
            for line in f_i:
                if flag1:
                    if line[:len2] == hint2:
                        splitted = line.split()
                        result.append(float(splitted[seq_no]))
                        flag1 = False
                    continue
                else:
                    if line[:len1] == hint1:
                        flag1 = True
        return sum(result)/len(result)

    def cal_accuracy(self,file_dir,
                     hint = ' inst#     actual  predicted error prediction',
                     num = 403):
        
        result = []
        no = 100
        with open(file_dir) as f_i:
            flag = False
            hint_len = len(hint)
            counter = 0;
            total = 0;
            for line in f_i:
                if flag:
                    if counter == 403:
                        flag = False
                        result.append((no,total/counter))
                        total = 0
                        counter = 0
                        no = no -1
                    else:
                        counter += 1
                        splitted = line.split()
                        gold = splitted[1].split(':')[1]
                        pred = splitted[2].split(':')[1]
                        if (gold == pred):
                            total += 1.0
                else:
                    if line[:hint_len] == hint:
                        flag = True
        return sorted(result,key=lambda x:x[1])
    def get_file_name(self,string):
        match = re.match('.*/(log.*).arff',string)
        return match.group(1)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        WekaSummary().readResult()
    if len(sys.argv) == 2:
        WekaSummary().readResult(sys.argv[1])

