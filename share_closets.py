from parse_arguments import parse_args
from poshmark_driver import PoshmarkDriver


def main():
    args = parse_args()

    poshmark_username, poshmark_password = PoshmarkDriver.get_login_credentials()

    # if args.self is selected, set the value of args.num_items to 0 (use all)
    num_items = 0 if args.self else args.num_items

    poshmark_driver = PoshmarkDriver(poshmark_username, args.pages, num_items)

    if args.self or args.account:
        '''
        If args.self is selected, share your own closet.
        If args.account is specified, use the seller value set using --account
        '''
        if args.self:
            seller = poshmark_username
        else:
            seller = args.account
        poshmark_driver.run_share_for_sellers(
            poshmark_password,
            seller=seller)
    else:
        '''
        Otherwise, default is to share items from the closets of the sellers you follow
        '''
        poshmark_driver.run_share_following_users(
            poshmark_password,
            args.num_accounts)



if __name__ == '__main__':
    main()
