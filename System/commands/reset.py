from System import Command
from datetime import datetime
import os
import shutil


class Reset(Command):
    """
    Resets the content from version of file.
    If version was not entered, the last committed version would be reset.
    """
    def run(self, full_request):
        for file in full_request.files:
            self.reset(full_request,
                       '{0}/{1}'.format(full_request.d, file))

    def reset(self, full_request, file):
        revision = full_request.rev
        if revision is None:
            revisions = self.find_all_revisions(full_request)
            for rev in revisions:
                if os.path.exists('{0}/repos/CVSROOT/{1}/{2}.c,v'
                                  .format(full_request.d, file, rev[:-1])):
                    revision = rev
        if revision is None:
            print("ERROR: File {0} was not committed!".format(file))
        elif not os.path.exists(file):
            print("ERROR: The entered file does not exist!")
        elif not os.path.exists("{0}/repos/CVSROOT/{1}/{2}.c,v"
                                .format(full_request.d, file, revision[:-1])):
            print("ERROR: This version of file does not exist!")
        else:
            if not full_request.n:
                shutil.copyfile("{0}/repos/CVSROOT/{1}/{2}.c,v"
                                .format(full_request.d, file, revision[:-1]),
                                file)
                if not full_request.l:
                    with open("{0}/repos/history.rcs".format(full_request.d),
                              'a') as history:
                        history.write('{0} {1} reset from revision {2}\n'
                                      .format(datetime.now(), file, revision))
            if not full_request.Q and not full_request.q:
                print('{0} reset from revision {1}'.format(file, revision))
