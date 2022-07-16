import math
import requests
import sqlite3
import snapshot_db

#init Hoverboard DB Connection
hoverboard_database = "hb_snapshot.db"
hb_conn = sqlite3.connect(hoverboard_database)
hbDB = snapshot_db.DB_HELPER
sql_create_hb_table = "CREATE TABLE IF NOT EXISTS Hoverboard_Snapshot (token_id string, wallet string, type string, modification string, color string);"
hbDB.create_table(hbDB, hb_conn, sql_create_hb_table)

#init Jetpack DB Connection
jetpack_database = "jp_snapshot.db"
jp_conn = sqlite3.connect(jetpack_database)
jpDB = snapshot_db.DB_HELPER
sql_create_jp_table = "CREATE TABLE IF NOT EXISTS Jetpack_Snapshot (token_id string, wallet string, type string, modification string, color string);"
jpDB.create_table(jpDB, jp_conn, sql_create_jp_table)

hb_contract = '0xeDa3b617646B5fc8C9c696e0356390128cE900F8'
jp_contract = '0xd0F0C40FCD1598721567F140eBf8aF436e7b97cF'
print("hb or jp snapshot?")
choice = input()
if choice == 'hb':
    contract = hb_contract
    offChainURL = 'https://api.jadu.ar/token/'
    conn = hb_conn
    DB = hbDB
    print('snapshotting hoverboards')
else:
    contract = jp_contract
    offChainURL = 'https://us-east1-jadu-e23c4.cloudfunctions.net/getJetPack?tokenId='
    conn = jp_conn
    DB = jpDB
    print('snapshotting jetpacks')

#Hit moralis token contract owners endpoint, fetch token ID & wallet address
onChainURL = f'https://deep-index.moralis.io/api/v2/nft/{contract}/owners'
headers = {'accept' : 'application/json', 'X-API-Key' : 'qJFFxHm5XSfa9jvGvdTXOm6Xu9UV90Be3rSe342lqRTxeXcFxEs40lG2QTomenFh'}
params = {'chain' : 'eth', 'format' : 'decimal'}
resp = requests.get(url=onChainURL, headers=headers, params=params)
onChainData = resp.json() 
pageLength = len(onChainData['result'])
contractSupply = onChainData['total']
pages = str(math.ceil(contractSupply / pageLength))
print('Beginning onchain data fetch loop. ' + pages + ' pages of length ' + str(pageLength))
while True:
    resp = requests.get(url=onChainURL, headers=headers, params=params)
    onChainData = resp.json() 
    pageLength = len(onChainData['result'])
    print('Getting token data using tokenIDs at page ' + str(onChainData.get('page')) + '/' + pages)
    for i in range(pageLength):
        tokenID = str(onChainData['result'][i]['token_id'])
        wallet = onChainData['result'][i]['owner_of']
        if DB.staking_check(DB, conn, tokenID, wallet):
            try:
                #using onchain token ID access off-chain metadata for that token, grab relevant values, add to tokenDict and append to dict_list)
                ocURL = offChainURL + tokenID
                resp = requests.get(url=ocURL)
                offChainData = resp.json()
                for attr in offChainData['attributes']:
                    match attr['trait_type']:
                        case "TYPE" | "1/1":
                            tokenTypeValue = attr['value']
                        case "COLOR":
                            tokenColorValue = attr['value']
                        case 'MODIFICATION':
                            tokenModValue = attr['value']            
            except:
                print('Unknown token issue')
                tokenTypeValue = "Error: Unknown uri metadata issue"
                tokenModValue = "Error: Unknown uri metadata issue"
                tokenColorValue = "Error: Unknown uri metadata issue"
                DB.update_token(DB, conn, tokenID, wallet, tokenTypeValue, tokenModValue, tokenColorValue)
                tokenTypeValue, tokenColorValue, tokenModValue = '','',''
            DB.update_token(DB, conn, tokenID, wallet, tokenTypeValue, tokenModValue, tokenColorValue)
            tokenTypeValue, tokenColorValue, tokenModValue = '','',''
        elif DB.wallet_check(DB, conn, tokenID, wallet):
            DB.update_owner(DB, conn, tokenID, wallet)
    if pages != str(onChainData.get('page')):
        params['cursor'] = onChainData.get('cursor')
        print('Finished fetching page ' + str(onChainData.get('page')) + ' data, going to next page')
    else:
        print('No more pages left')
        break