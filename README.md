# posh_share
A simple script to share Poshmark listings for yourself or for sellers you follow

# Script setup
The script expects a file called `credentials.py` to exist in the same directory as the `share_closets.py` script.
Please copy the `example_credentials.py` to `credentials.py` and replace the example login and password with your own. 
Do _not_ share or commit this file, this is not secure and is only suitable for running the script ad hoc/locally.

# Running the script
The share_closets.py script can be used for two main purposes:
1. To share all available listings from your own Poshmark closet, or 
2. To share some number of available listings from the closets of a subset of the Poshmark sellers you follow.

Examples

1. To share from your own closet, use the `--self` flag.  This will automatically find all available listings in your closet.
```commandline
python share_closets.py --self
```

2. To share 5 items from each of the closets of 20 of the sellers you follow, run the following:
```commandline
python share_closets.py --num_items 5 --num_accounts 20
```
