#!/usr/bin/env python3
"""Audit the seven genuine user-supplied FC courses whose pages were misregistered.

The input remains read-only. A course's pages being borrowed by other courses
does NOT make the course inauthentic; it is an unresolved source-integrity bug.
Use --strict as a release gate to prevent relabelling other FC pages as its own.
"""
import argparse, collections, json, pathlib, sys

RECOVERY_IDS=(
 "biocell_noyau","bio_proteines","bio_biomol",
 "chim_atoliais","chim_protons","phys_energie_elec","phys_fluides"
)

def audit(data):
    chapters={c["id"]:c for c in data.get("chapters",[])}
    if len(chapters)!=76 or not all(cid in chapters for cid in RECOVERY_IDS):
        raise ValueError("76 genuine course IDs and all seven recovery targets are mandatory")
    pages=data.get("coursePages",{})
    owners=collections.defaultdict(set)
    for cid in chapters:
        for page in pages.get(cid,[]):
            owners[page].add(cid)
    result=[]
    for cid in RECOVERY_IDS:
        page_list=pages.get(cid,[])
        unique=[p for p in page_list if owners[p]=={cid}]
        foreign=collections.Counter(other for p in page_list for other in owners[p] if other!=cid)
        result.append({
            "courseId":cid,"title":chapters[cid].get("title"),
            "sourcePageReferences":len(page_list),
            "uniquePageReferences":len(unique),
            "sharedPageReferences":len(page_list)-len(unique),
            "referencedOtherCourses":dict(foreign.most_common()),
            "releaseSourceStatus":"REQUIRES_ORIGINAL_FC_RECONCILIATION" if not unique else
                                  "SOME_UNIQUE_PAGES_PRESENT__MANUAL_FC_VERIFICATION_REQUIRED"
        })
    return {"courseCountPreserved":len(chapters),
            "noCourseDeleted":True,
            "allSevenOriginalCourseIDsPreserved":True,
            "independentFCSourceRecoveryComplete":False,
            "courseSourceEvidence":result}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True)
    ap.add_argument("--strict",action="store_true")
    args=ap.parse_args()
    data=json.loads(pathlib.Path(args.data).read_text(encoding="utf-8"))
    result=audit(data)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if args.strict and any(x["releaseSourceStatus"].startswith("REQUIRES")
                           for x in result["courseSourceEvidence"]):
        return 2
    return 0

if __name__=="__main__":
    try:sys.exit(main())
    except Exception as e:
        print(json.dumps({"passed":False,"reason":str(e)},ensure_ascii=False))
        sys.exit(3)
