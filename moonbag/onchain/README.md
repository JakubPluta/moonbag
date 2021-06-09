## How to use on-chain data menu
Currently there are two options to explore on-chain data.   
Moonbag supports ethereum explorer and terra explorer
- ethereum - explore on-chain data for ethereum [Ethplorer]
- terra - explore on-chain data for terra  [TerraAPI]


## Ethereum on-chain data 

### 1. token_info
show info about erc20 token [Ethplorer]   
required argument 
* -a, --address  [Token on-chain address]
```
token_info -a 0xa8b919680258d369114910511cc87595aec0be6d
```
### 2. tx_info 
show info about transaction on ethereum blockchain [Ethplorer]    
required argument 
* -a, --address [transaction on-chain address]
```
tx_info  -a 0x0836324289958ed2ed9e3b88f9538464ffa786358ada6ce956938213f9c30da2
```
### 3.  address_info  
show info about ethereum address [Ethplorer]   
required argument 
* -a, --address [on-chain address]
```
address_info  -a 0xa8b919680258d369114910511cc87595aec0be6d
```
### 4. address_tx  
show ethereum address transactions [Ethplorer]   
required argument 
* -a, --address [on-chain address]
```
address_tx -a 0xa8b919680258d369114910511cc87595aec0be6d
```
### 5. token_holders  
 show info about token holders [Ethplorer]     
required argument 
* -a, --address  [token on-chain address]
```
token_holders -a 0xa8b919680258d369114910511cc87595aec0be6d
```

### 6. token_price  
 show info about token price [Ethplorer]     
required argument 
* -a, --address  [token on-chain address]
```
token_price -a 0xa8b919680258d369114910511cc87595aec0be6d
```
### 7. token_hist  
show historical info about erc20 token [Ethplorer]      
required argument 
* -a, --address [token on-chain address]
```
token_hist -a 0xa8b919680258d369114910511cc87595aec0be6d
```
### 8. token_txs 
show info about historical token transactions [Ethplorer]       
required argument 
* -a, --address [token on-chain address]
```
token_txs  -a 0xa8b919680258d369114910511cc87595aec0be6d
```

#
## Luna Terra on-chain data 

### 1. transaction
show info about transaction [Terra]   
required argument 
* -a, --address [transaction on-chain address]
```
transaction -a F4A64FABEA21BE83B85AB3B599C13844F511CF7035E31D618BEBF614484EBC85
```

### 2. account_info
show info about terra account [Terra]   
required argument 
* -a, --address [account on-chain address]
```
account_info -a terra1vz0k2glwuhzw3yjau0su5ejk3q9z2zj4ess86s
```

### 3. staking
show info about staking [Terra]   
```
staking
```
### 4. supply 
show info about terra coins supply [Terra]   
```
supply 
```
### 5. validators 
show info about terra validators [Terra]   
```
validators 
```