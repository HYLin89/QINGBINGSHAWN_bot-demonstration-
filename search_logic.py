import json,os,sys

#path control & target json loading
def get_resource_path(relativePath):
    if hasattr(sys,'_MEIPASS'):
        base_path =sys._MEIPASS
    else:
        base_path =os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path,relativePath)

recipes_data=[]
invert_inx=[]

try:
    recipes_path=get_resource_path('recipes_tagged.json')
    with open(recipes_path,'r+',encoding='utf-8') as f:
        recipes_data=json.load(f)
    invert_inx_path=get_resource_path('inverted_index.json')
    with open(invert_inx_path,'r+',encoding='utf-8') as f:
        invert_inx=json.load(f)
    # print(f'loaded, theres total {len(recipes_data)} data')
except Exception as e:
    print(e)

#looking chart
recipe_map={}
for i in recipes_data:
    recipe_map[i['ID']]=i
# print(recipe_map)

def search_recipes(ingredients,start_idx=0,count=5):
    if (not ingredients or not invert_inx):
        return []
    #a scoreboard to write hits on every id 
    score_bd={}
    #iterate every ids to watch score each recipes
    for i in recipes_data:
        score_bd[i['ID']]=0
    for tag in ingredients:
        if tag in invert_inx:
            matchsID=invert_inx[tag]
            for sc in matchsID:
                score_bd[sc]+=1
    if (not score_bd):
        return []
    
    #sorted scores & take top 5s
    sorted_score=sorted(score_bd.items(),key=lambda x:x[1],reverse=True)
    results=[]

    #slicing (more data)
    total_results=len(sorted_score)
    sliced_scores=sorted_score[start_idx:start_idx+count]

    has_more=(start_idx+count)<total_results  #if there's more results

    for sc,score in sliced_scores:
        if (sc in recipe_map):
            recipe_info=recipe_map[sc]
            #copy of datas
            recipe_out=recipe_info
            recipe_out['match_score']=score
            results.append(recipe_out)
    return results,has_more

# a=search_recipes(['tomato','egg'])
# print(a)

