# Filename: cider.py
#
# Description: Describes the class to compute the CIDEr (Consensus-Based Image Description Evaluation) Metric
#               by Vedantam, Zitnick, and Parikh (http://arxiv.org/abs/1411.5726)
#
# Creation Date: Sun Feb  8 14:16:54 2015
#
# Authors: Ramakrishna Vedantam <vrama91@vt.edu> and Tsung-Yi Lin <tl483@cornell.edu>

from .cider_scorer import CiderScorer
import pdb

class Cider:
    """
    Main Class to compute the CIDEr metric

    """
    def __init__(self, test=None, refs=None, n=4, sigma=6.0):
        # set cider to sum over 1 to 4-grams
        self._n = n
        # set the standard deviation parameter for gaussian penalty
        self._sigma = sigma

    def compute_score(self, gts, res):
        """
        Main function to compute CIDEr score
        :param  hypo_for_image (dict) : dictionary with key <image> and value <tokenized hypothesis / candidate sentence>
                ref_for_image (dict)  : dictionary with key <image> and value <tokenized reference sentence>
        :return: cider (float) : computed CIDEr score for the corpus
        """

        assert(gts.keys() == res.keys())
        imgIds = gts.keys()

        cider_scorer = CiderScorer(n=self._n, sigma=self._sigma)

        class_refs = {}
        for key in imgIds:
            class_refs[key] = [id for id in imgIds if id.startswith(key[0:3]) and id != key]

        for id in imgIds:
            hypo = res[id]
            ref = gts[id]

            ref_class = []
            ref_class.append(ref)

            for class_ref in class_refs[id]:
                ref_class.append(gts[class_ref])

            # Sanity check.
            assert(type(hypo) is list)
            assert(len(hypo) == 1)
            assert(type(ref) is list)
            assert(len(ref) > 0)
            assert(type(ref_class) is list)
            assert(len(ref_class) > 0)

            cider_scorer += (hypo[0], ref, ref_class)

        score, scores = cider_scorer.compute_score()

        return score, scores

    def method(self):
        return "CIDEr"
