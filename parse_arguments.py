from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(description='Share items from one or more Poshmark closets')
    parser.add_argument("-p", "--pages", default=3, type=int,
        help="number of closet pages to scroll through")
    parser.add_argument("-n", "--num_items", default=0, type=int,
        help="Number of items to share for each closet (default=0 -> share all)")
    parser.add_argument("-f", "--num_accounts", default=10, type=int,
        help="Share from the closets of random number of sellers you follow (default 10)")
    parser.add_argument ('-s', '--self', action='store_true',
        help='Share your own closet (based on Poshmark username in credentials file)')
    return parser.parse_args()
