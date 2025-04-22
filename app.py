from flask import Flask,request,jsonify
import sqlite3

app = Flask(__name__) 
#初始化

def db_connect():
    '''
    建立資料庫連結
    '''
    conn = sqlite3.connect('database.db')
    #連結test.db這個資料庫文件
    conn.row_factory = sqlite3.Row
    #將檔案內欄位轉換成類dict的KEY-VALUE型態 ( 非正式dict )
    return conn

@app.route('/search',methods = ['GET'])
def get_order():
    conn = db_connect() #連接資料庫的函式
    cursor = conn.cursor() #建立一個鼠標

    name = request.args.get('name','')
    oid = request.args.get('oid','')
    start = request.args.get('start','')
    end = request.args.get('end','')
    #取得網址內的參數 (括號裡的參數名要對應網址的參數才抓的到)

    sql = '''
        select o.id,c.name customer,p.name product,o.quantity,o.order_date
        from orders o
        join customers c on o.customer_id = c.id
        join products p on o.product_id = p.id
        where 1=1
    '''
    #SQL語法
    #先寫好可重複使用sql這個變數,不用每次寫一大段,也能增加維護的便利性

    param = []
    if name:
        sql += ' and c.name = ?'
        param.append(name)
    if oid:
        sql += ' and o.id = ?'
        param.append(oid)
    if start:
        sql += ' and o.order_date >= ?'
        param.append(start)
    if end:
        sql += ' and o.order_date <= ?'
        param.append(end)
    #SQL條件參數區
    

    cursor.execute(sql,param) #執行SQL語法及帶入條件參數
    rows = cursor.fetchall() #將找到的資料全部抓回來
    conn.close() #關閉資料庫連線

    result = [dict(row) for row in rows]
    #因為row裡的資料是類dict,不是正式dict,不被jsonify接受
    #因此要使用dict()來將其轉換成真正的dict
    if not result:
        return jsonify({'message':'Data not found'}),404
    return jsonify(result),200
    #以json的格式回傳找到的資料

@app.route('/post',methods = ['POST'])
def post_order():
    data = request.get_json() #取得postman要新增的資料
    conn = db_connect()
    cursor = conn.cursor()


    sql = '''
        insert into orders (customer_id,product_id,quantity,order_date)
        values (?,?,?,?)
    '''
    #新增資料的SQL語法
    cursor.execute(sql,(
        data['customer_id'],
        data['product_id'],
        data['quantity'],
        data['order_date']
    )) #將postman裡要新增的資料放進參數位
    conn.commit() #SQL 提交
    conn.close()
    return jsonify({'message':'New data add success!'}),201

@app.route('/put/<int:oid>',methods=['PUT'])
def put_order(oid):
    data = request.get_json()
    conn = db_connect()
    cursor = conn.cursor()

    sql = '''
        update orders
        set customer_id = ?,product_id = ?,quantity = ?,order_date = ?
        where id = ?
    '''
    #修改資料的SQL語法
    cursor.execute(sql,(
        data['customer_id'],
        data['product_id'],
        data['quantity'],
        data['order_date']
        ,oid
    ))
    conn.commit()
    affected = cursor.rowcount #commit影響的列數
    conn.close()
    if affected == 0 : #如果commit沒有提交東西,則判定沒找到對應資料
        return jsonify({'message':f'ID: {oid} data not found'}),404
    return jsonify({'message':'Data update success!'}),200

@app.route('/patch/<int:oid>',methods=['PATCH'])
def patch_order(oid):
    data = request.get_json()
    conn = db_connect()
    cursor = conn.cursor()

    field = []
    param = []

    if 'customer_id' in data:
        field.append("customer_id = ?")
        param.append(data['customer_id'])
    if 'product_id' in data:
        field.append("product_id = ?")
        param.append(data['product_id'])
    if 'quantity' in data:
        field.append("quantity = ?")
        param.append(data['quantity'])
    if 'order_date' in data:
        field.append("order_date = ?")
        param.append(data['order_date'])
    
    if not field:
        return jsonify({'message':f'ID: {oid} Data not found or Data no needs to update!'}),404
    sql = f'''
        update orders set {", ".join(field)} where id =?
    '''
    #修改部分資料的SQL語法
    param.append(oid)
    cursor.execute(sql,param)

    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected == 0:
        return jsonify({'message':f'ID: {oid} Data not found or Data no needs to update!'}),404
    return jsonify({'message':'Data update success!'}),200

@app.route('/del/<int:oid>',methods=['DELETE'])
def del_order(oid):
    conn = db_connect()
    cursor = conn.cursor()

    sql = '''
        delete from orders where id = ?
    '''
    #刪除資料的SQL語法

    cursor.execute(sql,(oid,))

    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected == 0 :
        return jsonify({'message':f'ID: {oid} data not found'}),404
    return jsonify({'message':'Data delete success!'}),200



if __name__ == '__main__':
    app.run(debug=True)