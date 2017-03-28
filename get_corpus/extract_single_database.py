import pymysql

def main():
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='data1', charset='utf8')
    cursor = conn.cursor()

    sql = "select label,question, answer from `data1`.corpus"
    cursor.execute(sql)
    data = cursor.fetchall()

    with open("data1_corpus.txt","a",encoding="utf8") as fp:
        for i in data:
            fp.writelines(str(list(i))+"\n")

if __name__ =="__main__":
    main()