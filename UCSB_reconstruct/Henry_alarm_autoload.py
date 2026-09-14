import pandas as pd
import os, copy
import Henry_env as sec


class Alarm_Setting():
    def __init__(self):
        super().__init__()
        # self.currentdir = os.getcwd()
        self.currentdir ="/home/hep/.config/sbcconfig/"
        self.address = 'sbc_alarm_config.csv'
        self.fulladdress = os.path.join(self.currentdir, self.address)
        self.instrument=[]
        self.highlimit = []
        self.lowlimit = []
        self.active = []
        self.dtype = []

    def initialize(self):
        self.TT_AD1_LowLimit = copy.copy(sec.TT_AD1_LOWLIMIT)
        self.TT_AD1_HighLimit = copy.copy(sec.TT_AD1_HIGHLIMIT)
        self.TT_AD2_LowLimit = copy.copy(sec.TT_AD2_LOWLIMIT)
        self.TT_AD2_HighLimit = copy.copy(sec.TT_AD2_HIGHLIMIT)
        self.HTRTD_LowLimit  = copy.copy(sec.HTRTD_LOWLIMIT)
        self.HTRTD_HighLimit = copy.copy(sec.HTRTD_HIGHLIMIT)
        self.PT_LowLimit = copy.copy(sec.PT_LOWLIMIT)
        self.PT_HighLimit = copy.copy(sec.PT_HIGHLIMIT)
        self.LL_HighLimit = copy.copy(sec.LL_HIGHLIMIT)
        self.LL_LowLimit = copy.copy(sec.LL_LOWLIMIT)
        self.LOOPPID_HI_LIM = copy.copy(sec.LOOPPID_ALARM_HI_LIM)
        self.LOOPPID_LO_LIM = copy.copy(sec.LOOPPID_ALARM_LO_LIM)

        self.TT_AD1_Activated = copy.copy(sec.TT_AD1_ACTIVATED)
        self.TT_AD2_Activated = copy.copy(sec.TT_AD2_ACTIVATED)
        self.HTRTD_Activated = copy.copy(sec.HTRTD_ACTIVATED)
        self.PT_Activated = copy.copy(sec.PT_ACTIVATED)
        self.LL_Activated = copy.copy(sec.LL_ACTIVATED)
        self.LOOPPID_Activated = copy.copy(sec.LOOPPID_ACTIVATED)


        # lowlimit, high limit and activae share the same keys
        for key in self.TT_AD1_LowLimit:
            self.instrument.append(key)
            self.lowlimit.append(self.TT_AD1_LowLimit[key])
            self.highlimit.append(self.TT_AD1_HighLimit[key])
            self.active.append(self.TT_AD1_Activated[key])


        for key in self.TT_AD2_LowLimit:
            self.instrument.append(key)
            self.lowlimit.append(self.TT_AD2_LowLimit[key])
            self.highlimit.append(self.TT_AD2_HighLimit[key])
            self.active.append(self.TT_AD2_Activated[key])

        for key in self.PT_LowLimit:
            self.instrument.append(key)
            self.lowlimit.append(self.PT_LowLimit[key])
            self.highlimit.append(self.PT_HighLimit[key])
            self.active.append(self.PT_Activated[key])

        for key in self.LL_LowLimit:
            self.instrument.append(key)
            self.lowlimit.append(self.LL_LowLimit[key])
            self.highlimit.append(self.LL_HighLimit[key])
            self.active.append(self.LL_Activated[key])

        for key in self.LOOPPID_LO_LIM:
            self.instrument.append(key)
            self.lowlimit.append(self.LOOPPID_LO_LIM[key])
            self.highlimit.append(self.LOOPPID_HI_LIM[key])
            self.active.append(self.LOOPPID_Activated[key])

        for key in self.HTRTD_LowLimit:
            self.instrument.append(key)
            self.lowlimit.append(self.HTRTD_LowLimit[key])
            self.highlimit.append(self.HTRTD_HighLimit[key])
            self.active.append(self.HTRTD_Activated[key])


        self.init_dic = {"Instrument":self.instrument, "Low_Limit":self.lowlimit, "High_Limit":self.highlimit, "Active":self.active}


    def read_Information(self):
        self.df = pd.read_csv(self.fulladdress)
        # print(self.df.head(5))
        # print(self.df.iloc[0]["High_Limit"],type(self.df.iloc[0]["High_Limit"]))
        self.low_dic = self.translate_csv("Low_Limit")
        self.high_dic = self.translate_csv("High_Limit")
        self.active_dic = self.translate_csv("Active")
    # csv file will lose the data type of the record, we need to recover those properties
    def translate_csv(self, type="Low_Limit"):
        df = self.df[["Instrument",type]]
        dic = df.set_index('Instrument').T.to_dict('records')[0]
        # print("before",dic)
        for key in dic:
            try:
                dic[key] = float(dic[key])
            except:
                if (dic[key] == "FALSE") or (dic[key] =="False"):
                    dic[key] = False
                elif (dic[key] =="TRUE") or (dic[key] =="True"):
                    dic[key] = True
                else:
                    pass

        # print("after",dic)
        return dic

    def write(self):
        self.initialize()
        # print(type(self.init_dic["Low_Limit"][0]))
        df = pd.DataFrame(self.init_dic)
        # df = pd.DataFrame(columns=["Instrument","LowLimit","HighLimit","Active"])

        df.to_csv(self.fulladdress, index=False)


if __name__=="__main__":
    AS= Alarm_Setting()
    AS.initialize()
    AS.write()
    # AS.read_Information()