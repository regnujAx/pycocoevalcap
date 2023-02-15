#!/usr/bin/env python

# Python wrapper for METEOR implementation, by Xinlei Chen
# Acknowledge Michael Denkowski for the generous discussion and help

import os
import subprocess
import threading

# Assumes meteor-1.5.jar is in the same directory as meteor.py. Change as needed.
METEOR_JAR = 'meteor-1.5.jar'

class Meteor:

    def __init__(self):
        # Java uses as locale settings the default locale of your system/OS.
        # Depending on your locale settings (e.g., if you live in Germany) it is possible
        # that float conversion of score_string (see compute_score below)
        # throws the ValueError "could not convert string to float: b''"
        # because of wrong interpretation of the decimal separator in eval_line.
        # To set the locale for Java independent of the default locale,
        # it is necessary to add a new environment variable that Java knows and can use.
        # This must be done before starting the subprocess.
        os.environ["JAVA_TOOL_OPTIONS"] = "-Duser.language=en -Duser.country=US"
        # Another option would be to set the used locale in Java (in this case OpenJDK)
        # with the shell-command
        #   export JAVA_TOOL_OPTIONS="-Duser.language=en -Duser.country=US"
        # However, setting the Java locale in this way works only in the shell in which the command was executed.
        # If you close the shell or open a new one, you have to run the command again.

        self.meteor_cmd = ['java', '-jar', '-Xmx2G', METEOR_JAR, '-', '-', '-stdio', '-l', 'en', '-norm']
        self.meteor_p = subprocess.Popen(
            self.meteor_cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        # Used to guarantee thread safety
        self.lock = threading.Lock()

    def compute_score(self, gts, res):
        assert(gts.keys() == res.keys())
        imgIds = gts.keys()
        scores = []

        eval_line = 'EVAL'
        self.lock.acquire()
        for i in imgIds:
            assert(len(res[i]) == 1)
            stat = self._stat(res[i][0], gts[i])
            eval_line += ' ||| {}'.format(stat)

        self.meteor_p.stdin.write('{}\n'.format(eval_line).encode())
        self.meteor_p.stdin.flush()
        while len(scores) <= len(imgIds):
            score_string = self.meteor_p.stdout.readline().strip()
            score_strings = score_string.split()
            for s in score_strings:
                score = float(s)
                scores.append(score)
        score = scores[-1]
        self.lock.release()

        return score, scores

    def method(self):
        return "METEOR"

    def _stat(self, hypothesis_str, reference_list):
        # SCORE ||| reference 1 words ||| reference n words ||| hypothesis words
        hypothesis_str = hypothesis_str.replace('|||', '').replace('  ', ' ')
        score_line = ' ||| '.join(('SCORE', ' ||| '.join(reference_list), hypothesis_str))
        self.meteor_p.stdin.write('{}\n'.format(score_line).encode())
        self.meteor_p.stdin.flush()
        return self.meteor_p.stdout.readline().decode().strip()

    def __del__(self):
        self.lock.acquire()
        self.meteor_p.stdin.close()
        self.meteor_p.kill()
        self.meteor_p.wait()
        self.lock.release()
