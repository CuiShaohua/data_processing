import pandas as pd



if __name__ == "__main__":

    df_origin = pd.read_excel("LiJinshan.xlsx", )
    #print(df_origin["Publisher"])
    df_info = pd.read_excel("IF1.xlsx")
    dictionary1 = dict(zip(list(df_info["期刊名称"]), list(df_info["影响因子"])))
    dictionary2 = dict(zip(list(df_info["期刊名称"]), list(df_info["分区"])))
    #print(df_info["Journal Impact Factor"])
    IF, JCR = [],[]
    for i in list(df_origin["Publisher"]):
        if i in dictionary1.keys():
            IF.append(dictionary1[i])
            JCR.append(dictionary2[i])
        else:
            IF.append(None)
            JCR.append(None)

    df_origin["IFS"] = IF
    df_origin["JCR"] = JCR
    df_origin = df_origin[["Title","Author1","Author2","Author3" "Keywords", "Abstract", "Publisher", "IFS", "JCR", "PublisherTime", "BaiduXueShuLink","PaperDOI", "CitationNum", "AvailDownloadLinks"]]
    writer = pd.ExcelWriter('LiJinshanPaperInfo.xlsx')
    df_origin.to_excel(writer, sheet_name='Info', startcol=0, index=False)
    writer.save()
