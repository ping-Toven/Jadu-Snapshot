import requests
import math
import pandas

token_dict_list = []
#Hit moralis token contract owners endpoint, fetch token ID & wallet address
onChainURL = 'https://deep-index.moralis.io/api/v2/nft/0xeDa3b617646B5fc8C9c696e0356390128cE900F8/owners'
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
        tokenDict['token ID'] = int(onChainData['result'][i]['token_id'])
        tokenDict['wallet address'] = onChainData['result'][i]['owner_of']
        tokenTypeValue, tokenColorValue, tokenModValue = '','',''
        try:
            #using onchain token ID access off-chain metadata for that token, grab relevant values, add to tokenDict and append to dict_list)
            tokenID = str(onChainData['result'][i]['token_id'])
            offChainURL = 'https://api.jadu.ar/token/' + tokenID
            resp = requests.get(url=offChainURL)
            offChainData = resp.json()
            for attr in offChainData['attributes']:
                if attr['trait_type'] == "TYPE":
                    tokenTypeValue = attr['value']
                if attr['trait_type'] == "1/1":
                    tokenTypeValue = attr['value']                    
                if attr['trait_type'] == "MODIFICATION":
                    tokenModValue = attr['value']
                if attr['trait_type'] == "COLOR":
                    tokenColorValue = attr['value']
        except:
            print('Unknown token issue')
            tokenDict['token Type'] = "Error: Unknown uri metadata issue"
            tokenDict['token Modification'] = "Error: Unknown uri metadata issue"
            tokenDict['token Color'] = "Error: Unknown uri metadata issue"
            token_dict_list.append(tokenDict)
            continue
        tokenDict['token Type'] = tokenTypeValue
        tokenDict['token Modification'] = tokenModValue
        tokenDict['token Color'] = tokenColorValue
        token_dict_list.append(tokenDict)
        tokenTypeValue, tokenModValue, tokenColorValue = '','',''
    if pages != str(onChainData.get('page')):
        params['cursor'] = onChainData.get('cursor')
        print('Finished fetching page ' + str(onChainData.get('page')) + ' data, going to next page')
    else:
        print('No more pages left')
        break

#create panda df with tokenDict as a list
print('creating df')
hoverboardData = pandas.DataFrame(token_dict_list)
print('dumping')
hoverboardData.to_csv('HoverboardData.csv')
print('done')