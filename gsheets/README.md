# gsheets
## setup
Put credentials.json in `config` dir

## set in sheets:
```
=if(B2="","",A1+1)
```
or
```
=if(B2="","",ROW()-1)
```
or
```
=if(COUNTA(B2:P2)>0,ROW()-1,"")
```