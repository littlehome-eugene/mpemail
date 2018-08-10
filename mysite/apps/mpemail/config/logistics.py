import csv

def get_logistics_info(start_date, end_date):
    with open('logistics_data.csv') as f:
        csv_reader = csv.reader(f, delimiter=',', quotechar='"')
        data = []
        no = 0
        for line in csv_reader:
            no += 1
            if no == 1:
                continue
            one_data = {}
            one_data['order_no'] = line[0]
            one_data['logis_no'] = line[1]
            one_data['name'] = line[2]
            one_data['home_phone'] = line[3]
            one_data['mobile'] = line[4]
            one_data['safe_phone'] = line[5]
            one_data['product'] = line[6]
            one_data['addr'] = line[7]
            one_data['zip'] = line[8]
            one_data['sender_name'] = line[9]
            one_data['sender_home_phone'] = line[10]
            one_data['sender_mobile'] = line[11]
            one_data['delivery_status'] = line[12]
            one_data['delivery_detail'] = line[13]
            one_data['print_date'] = line[14]
            one_data['delivery_start_date'] = line[15]
            one_data['delivery_end_date'] = line[16]
            one_data['box_no'] = line[17]
            one_data['box_type'] = line[18]
            one_data['price'] = line[19]
            one_data['additional_price'] = line[20]
            one_data['etc'] = line[21]

            if one_data['print_date'] >= start_date and one_data['print_date'] <= end_date:
                data.append(one_data)
        
        return data


if __name__ == '__main__':
    data = get_logistics_info('20180716', '20180717')
    
    print 'no: %s' % len(data)
    print 'order_no: %s' % data[3]['order_no']
    print 'logis_no: %s' % data[3]['logis_no']
    print 'name: %s' % data[3]['name']
    print 'home_phone: %s' % data[3]['home_phone']
    print 'mobile: %s' % data[3]['mobile']
    print 'safe_phone: %s' % data[3]['safe_phone']
    print 'product: %s' % data[3]['product']
    print 'addr: %s' % data[3]['addr']
    print 'zip: %s' % data[3]['zip']
    print 'sender_name: %s' % data[3]['sender_name']
    print 'sender_home_phone: %s' % data[3]['sender_home_phone']
    print 'sender_mobile: %s' % data[3]['sender_mobile']
    print 'delivery_status: %s' % data[3]['delivery_status']
    print 'delivery_detail: %s' % data[3]['delivery_detail']
    print 'print_date: %s' % data[3]['print_date']
    print 'delivery_start_date: %s' % data[3]['delivery_start_date']
    print 'delivery_end_date: %s' % data[3]['delivery_end_date']
    print 'box_no: %s' % data[3]['box_no']
    print 'box_type: %s' % data[3]['box_type']
    print 'price: %s' % data[3]['price']
    print 'additional_price: %s' % data[3]['additional_price']
    print 'etc: %s' % data[3]['etc']
    
    