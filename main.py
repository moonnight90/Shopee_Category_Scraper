
from Asy import Asynio_Requests
import pandas as pd
import requests,os,json
import nest_asyncio

nest_asyncio.apply()
obj = Asynio_Requests()

INPUT_FILE_PATH = "Input_Cats.xlsx"
OUTPUT_FILE_PATH = "Product_Data.csv"

domain="sg"
cat_key = "match_id"

def url_generator(item):
    url = f"https://shopee.{domain}/"
    name = item['item_basic']['name'].replace(" ",'-').replace(' / ','-').replace(r"\n",' ')
    url += name+f"-i.{item['shopid']}.{item['itemid']}"
    return url

def parse_results(results,url):
    global Counter
    main_list = []
    for result in results:    
        items = result['items']
        for item_m in items:
            temp = {}
            item = item_m['item_basic']
            temp["Title"] = item['name'].replace(r"\n",' ')
            temp['Price Min'] = "%.2f" % (item['price_min']/100000)
            temp['Price Max'] = "%.2f" % (item['price_max']/100000)
            temp['Monthly Sold'] = item['sold']
            temp['Country'] = item['shop_location']
            temp['Total Sales'] = item['historical_sold']
            temp['Total Ratings'] = item['item_rating']['rating_count'][0]
            temp['Rating'] = "%.2f" % item['item_rating']['rating_star']
            temp['Shop ID'] = item['shopid']
            temp['Listing URL'] = url_generator(item_m)
            temp['Category URL'] = url
            main_list.append(temp)
            Counter+=1
            print(Counter,temp['Title'])
    return main_list
# 
def run(match_id,page,url):
    global header,main_df
    temp_list = []
    for page in range(6):
        params = {'by': 'sales','limit': '100',cat_key: f"{match_id}",'newest': page*100,'order': 'desc','page_type': 'search','scenario': 'PAGE_CATEGORY','version': '2',}
        temp_list.append({'params':params,'url':f'https://shopee.{domain}/api/v4/search/search_items/'})
    obj.add_links(temp_list)
    ress = obj.run()
    results = parse_results(ress,url)
    pd.DataFrame(results).to_csv(OUTPUT_FILE_PATH,mode='a',encoding="UTF-8",errors="ignore",index=False,header=header)
    # new_df = pd.DataFrame(results)
    # main_df = pd.concat([main_df,new_df])
    # main_df.to_excel(OUTPUT_FILE_PATH,index=False)
    header=False
    
def load_categories():
    records = pd.read_excel(INPUT_FILE_PATH).to_records()
    return records

def get_sub_catgories(catid):
    res = requests.get(f"https://shopee.{domain}/api/v4/pages/get_category_tree").json()
    for i in res['data']['category_list']:
        if int(catid) ==  i['catid']:
            print(i['name'])
            return i['children']

def main(cat_id):
    global logs
    childrens = get_sub_catgories(cat_id)
    start=False
    if None == childrens: childrens = [{"catid":cat_id,"name":"Manual Input"}]
    if logs['child_cat'] == "finished" or logs['child_cat'] == None: start = True
    for child in childrens:
        child_id = child['catid']
        if child_id ==logs['child_cat'] and start==False:
            start = True
            continue
        if not start: continue
        print("\nScraping \"{}\"".format(child['name']))
        
        cat_url = f"https://shopee.{domain}/"+child["name"].replace(' ','-')+f"-cat.{cat_id}.{child_id}"
        # for i in range(30):
        run(child_id,"i",cat_url)
        logs = save_load_logs({"main_cat":cat_id,"child_cat":child_id})
    logs = save_load_logs({"main_cat":cat_id,"child_cat":"finished"})

def set_domain(cat:str):
    global domain,cat_key
    if cat.find("shopee.tw")>-1: domain = "tw"; cat_key = "fe_categoryids"
    else: domain = "sg"; cat_key = "match_id"


def save_load_logs(logs=None):
    global start
    if logs== None:
        
        ### Loading Logs
        logs = {"main_cat":None,"child_cat":None}
        if os.path.exists('logs'):            
            if input("Do you want to continue from previous stop(y/n)?").lower()=="y":
                start = False
                with open('logs') as f: logs = json.loads(f.read())                
        return logs
    else:

        ### Saving Logs

        with open('logs','w') as f: f.write(json.dumps(logs))
        return logs


if __name__ == "__main__":

    # if os.path.exists(OUTPUT_FILE_PATH):
    #     main_df = pd.read_excel(OUTPUT_FILE_PATH)
    # else: main_df = pd.DataFrame()
    
    cats = load_categories()
    logs = save_load_logs()
    header = True
    Counter=0
    start = True
    for cat in cats:
        if cat[1] == logs['main_cat']: 
            start=True
            if logs['child_id'] == "finished": continue
        if False == start: continue
        if cat[2]==True:
            set_domain(cat[1])
            cat_id = cat[1].split("?")[0].split('.')[-1]
            main(cat_id)    
    os.remove('logs')


