from Scripts import *
import os, plistlib

class OCCC:
    def __init__(self):
        self.d = downloader.Downloader()
        self.u = utils.Utils("OC Config Compare")
        if 2/3 == 0: self.dict_types = (dict,plistlib._InternalDict)
        else: self.dict_types = (dict)
        self.current_config = None
        self.current_plist  = None
        self.sample_plist   = None
        self.sample_url     = "https://github.com/acidanthera/OpenCorePkg/raw/master/Docs/Sample.plist"
        self.sample_path    = os.path.join(os.path.dirname(os.path.realpath(__file__)),os.path.basename(self.sample_url))
        self.sample_config  = self.sample_path if os.path.exists(self.sample_path) else None
        if self.sample_config:
            try:
                with open(self.sample_config,"rb") as f:
                    self.sample_plist = plist.load(f)
            except:
                self.sample_plist = self.sample_config = None

    def compare(self):
        # First make sure we have plist info
        if self.current_plist is None:
            p = self.get_plist("user config.plist")
            if p is None:
                return
            self.current_config,self.current_plist = p
        if self.sample_plist is None:
            p = self.get_latest(False)
            if p is None:
                return
            self.sample_config,self.sample_plist = p
        self.u.head()
        print("")
        print("Checking for values missing from User plist:")
        print("")
        changes = self.compare_value(self.sample_plist,self.current_plist,os.path.basename(self.current_config))
        if len(changes):
            print("\n".join(changes))
        else:
            print(" - Nothing missing from User config!")
        print("")
        print("Checking for values missing from Sample:")
        print("")
        changes = self.compare_value(self.current_plist,self.sample_plist,os.path.basename(self.sample_config))
        if len(changes):
            print("\n".join(changes))
        else:
            print(" - Nothing missing from Sample config!")
        print("")
        self.u.grab("Press [enter] to return...")

    def compare_value(self, compare_from, compare_to, path=""):
        change_list = []
        # Compare 2 collections and print anything that's in compare_from that's not in compare_to
        if type(compare_from) != type(compare_to):
            change_list.append("{} - Type Difference: {} --> {}".format(path,type(compare_to),type(compare_from)))
            return change_list # Can't compare further - they're not the same type
        if isinstance(compare_from,self.dict_types):
            # Let's compare keys
            not_keys = [x for x in list(compare_from) if not x in list(compare_to)]
            if not_keys:
                for x in not_keys:
                    change_list.append("{} - Missing Key: {}".format(path,x))
            # Let's verify all other values if needed
            for x in list(compare_from):
                if x in not_keys: continue # Skip these as they're already not in the _to
                val = compare_from[x]
                if isinstance(val,list) or isinstance(val,self.dict_types):
                    change_list.extend(self.compare_value(val,compare_to[x],path+" -> "+x))
        elif isinstance(compare_from,list):
            # This will be tougher, but we should only check for dict children and compare keys
            if not len(compare_from) or not len(compare_to): return change_list # Nothing to do here
            if isinstance(compare_from[0],self.dict_types):
                # Let's compare keys
                change_list.extend(self.compare_value(compare_from[0],compare_to[0],path+" -> "+"Array"))
        return change_list

    def get_latest(self,wait=True):
        self.u.head()
        print("")
        print("Gathering latest Sample.plist from:")
        print(self.sample_url)
        print("")
        p = None
        dl_config = self.d.stream_to_file(self.sample_url,self.sample_path)
        if not dl_config:
            print("\nFailed to download!\n")
            if wait: self.u.grab("Press [enter] to return...")
            return None
        print("Loading...")
        try:
            with open(dl_config,"rb") as f:
                p = plist.load(f)
        except Exception as e:
            print("\nPlist failed to load:  {}\n".format(e))
            if wait: self.u.grab("Press [enter] to return...")
            return None
        print("")
        if wait: self.u.grab("Press [enter] to return...")
        return (dl_config,p)

    def get_plist(self,plist_name="config.plist"):
        while True:
            self.u.head()
            print("")
            print("M. Return to Menu")
            print("Q. Quit")
            print("")
            m = self.u.grab("Please drag and drop the {} file:  ".format(plist_name))
            if m.lower() == "m":
                return None
            elif m.lower() == "q":
                self.u.custom_quit()
            pl = self.u.check_path(m)
            if not pl:
                self.u.head()
                print("")
                self.u.grab("That path does not exist!",timeout=5)
                continue
            try:
                with open(pl,"rb") as f:
                    p = plist.load(f)
            except Exception as e:
                self.u.head()
                print("")
                self.u.grab("Plist failed to load:  {}".format(e),timeout=5)
                continue
            return (pl,p) # Return the path and plist contents

    def main(self):
        self.u.head()
        print("")
        print("Current Config:   {}".format(self.current_config))
        print("OC Sample Config: {}".format(self.sample_config))
        print("")
        print("1. Get Latest Sample.plist")
        print("2. Select Custom Sample.plist")
        print("3. Select User Config.plist")
        print("4. Compare (will use latest Sample.plist if none selected)")
        print("")
        print("Q. Quit")
        print("")
        m = self.u.grab("Please select an option:  ").lower()
        if m == "q":
            self.u.custom_quit()
        elif m == "1":
            p = self.get_latest()
            if p is not None:
                self.sample_config,self.sample_plist = p
        elif m == "2":
            p = self.get_plist("OC Sample.plist")
            if p is not None:
                self.sample_config,self.sample_plist = p
        elif m == "3":
            p = self.get_plist("user config.plist")
            if p is not None:
                self.current_config,self.current_plist = p
        elif m == "4":
            self.compare()

if __name__ == '__main__':
    if 2/3 == 0:
        input = raw_input
    o = OCCC()
    while True:
        try:
            o.main()
        except Exception as e:
            print("\nError: {}\n".format(e))
            input("Press [enter] to continue...")
