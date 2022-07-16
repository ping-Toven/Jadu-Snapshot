import math
import requests
import pandas

token_dict_list = []
#Hit moralis token contract owners endpoint, fetch token ID & wallet address
onChainURL = 'https://deep-index.moralis.io/api/v2/nft/0xd0F0C40FCD1598721567F140eBf8aF436e7b97cF/owners'
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
        tokenDict = {}
        int_tokenID = int(onChainData['result'][i]['token_id'])
        tokenID = str(onChainData['result'][i]['token_id'])
        tokenDict['tokenID'] = int_tokenID
        tokenDict['wallet address'] = onChainData['result'][i]['owner_of']
        try:
            #using onchain token ID access off-chain metadata for that token, grab relevant values, add to tokenDict and append to dict_list)
            offChainURL = 'https://us-east1-jadu-e23c4.cloudfunctions.net/getJetPack?tokenId=' + tokenID
            resp = requests.get(url=offChainURL)
            offChainData = resp.json()
            for attr in offChainData['attributes']:
                match attr['trait_type']:
                    case "TYPE":
                        tokenTypeValue = attr['value']
                    case "COLOR":
                        tokenColorValue = attr['value']
                    case 'MODIFICATION':
                        tokenModValue = attr['value']   
                    case _:
                        tokenTypeValue, tokenModValue, tokenColorValue = 'Error 404', 'Error 404', 'Error 404'                
        except:
            print('Unknown token issue')
            tokenDict['token Type'] = "Error: Unknown uri metadata issue"
            tokenDict['token Mods'] = "Error: Unknown uri metadata issue"
            tokenDict['token Color'] = "Error: Unknown uri metadata issue"
        tokenDict['token Type'] = tokenTypeValue
        tokenDict['token Mods'] = tokenModValue
        tokenDict['token Color'] = tokenColorValue
        token_dict_list.append(tokenDict)
        tokenTypeValue, tokenColorValue, tokenModValue = '','',''
    if pages != str(onChainData.get('page')):
        params['cursor'] = onChainData.get('cursor')
        print('Finished fetching page ' + str(onChainData.get('page')) + ' data, going to next page')
    else:
        print('No more pages left')
        break

#create panda df with tokenDict as a list, headers = index,tokenID,wallet address,tokenType
print('creating df')
jetpack_df = pandas.DataFrame(token_dict_list)
#some janky ass groupby operation that doesn't work
#jp_df_by_Wallet = pandas.read_csv('JetpackData.csv', header=0, names=['tokenID','wallet address','tokenType'], index_col=False)
#jp_df_by_Wallet = pandas.DataFrame(jp_df_by_Wallet.groupby(by="wallet address"))

print('dumping')
jetpack_df.to_csv('JetpackData.csv')
print('done')