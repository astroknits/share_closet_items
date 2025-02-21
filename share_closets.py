from parse_arguments import parse_args
from poshmark_driver import PoshmarkDriver
from community_sharer import CommunitySharer
from self_sharer import SelfSharer

def main():
    args = parse_args()

    poshmark_username, poshmark_password = PoshmarkDriver.get_login_credentials()

    # if args.self is selected, set the value of args.num_items to 0 (use all)
    num_items = 0 if args.self else args.num_items

    if args.self:
        '''
        If args.self is selected, share your own closet.
        '''
        driver = SelfSharer(poshmark_username)
        driver.run(poshmark_password)
    else:
        '''
        Otherwise, share items from the closets of the sellers you follow
        '''
        driver = CommunitySharer(poshmark_username, args.pages, num_items)
        driver.run(poshmark_password, args.num_accounts)



if __name__ == '__main__':
    main()
