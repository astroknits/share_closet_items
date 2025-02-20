from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(description='Share items from one or more Poshmark closets')
    parser.add_argument("-t", "--time", default=1, type=int,
        help=('loop time in hours to repeat the code'))
    parser.add_argument("-p", "--pages", default=3, type=int,
        help="number of closet pages to scroll through")
    parser.add_argument("-n", "--num_items", default=0, type=int,
        help="Number of items to share for each closet (default=0 -> share all)")
    parser.add_argument("-a", "--account", type=str, default=None,
        help=('the poshmark closet account to share'))
    parser.add_argument("-f", "--following", default=0, type=int,
        help="Share from the closets of random number of sellers you follow (default 0 = share all)")
    parser.add_argument ('-s', '--self', action='store_true',
        help='Share your own closet (based on poshmark username in credentials file)')
    return parser.parse_args()
