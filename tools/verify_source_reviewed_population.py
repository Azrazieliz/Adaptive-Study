#!/usr/bin/env python3
"""Verify scoped, source-image-reviewed study records against an original FC APK.

Checks IDs, source hashes, answer/rationale integrity and the exact allowed
change set. It cannot certify medical/scientific accuracy without visual review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

FAKE = {"histo_embryo","biocell_cytosq","biocell_mec_integrine","biocell_dev","biocell_cycle"}

def indexed(records, kind):
    d={}
    for row in records:
        key=row.get("id")
        if not isinstance(key,str) or not key or key in d:
            raise ValueError(f"{kind}: missing/duplicate ID {key}")
        d[key]=row
    return d

def inspect(before,after,apk):
    findings=[]
    originals=indexed(before["chapters"],"base chapters")
    current=indexed(after["chapters"],"candidate chapters")
    if originals!=current or len(current)!=76 or FAKE.intersection(current):
        raise ValueError("Course identity or genuine-course count was changed")
    exempt={"questions","flashcards","courseGuides"}
    for field in set(before)|set(after):
        if field not in exempt and before.get(field)!=after.get(field):
            raise ValueError(f"Unrelated root field {field} has changed")
    with zipfile.ZipFile(apk) as z:
        for kind,prefix in [("questions","source26:"),("flashcards","source26:")]:
            base=indexed(before[kind],kind+" original")
            candidate=indexed(after[kind],kind+" candidate")
            for rid,original in base.items():
                if candidate.get(rid)!=original:
                    raise ValueError(f"{kind}: source record changed {rid}")
            for rid,item in candidate.items():
                if rid in base:continue
                if not rid.startswith(prefix):
                    raise ValueError(f"{kind}: unapproved ID {rid}")
                cid=item.get("chapterId")
                page=item.get("source",{}).get("page") if kind=="questions" else item.get("page")
                if cid not in current or not isinstance(page,int) or not 1<=page<=len(after["coursePages"][cid]):
                    raise ValueError(f"{kind}: invalid chapter or page {rid}")
                source_path=after["coursePages"][cid][page-1]
                sha=hashlib.sha256(z.read("assets/www/"+source_path)).hexdigest()
                if kind=="questions":
                    src=item.get("source",{})
                    if (src.get("image")!=source_path or src.get("sha256")!=sha or
                        src.get("kind")!="ORIGINAL_FC_IMAGE" or
                        item.get("studyQuestionStatus")!="APPROVED_SOURCE_IMAGE_REVIEW_20261112"):
                        raise ValueError(f"{rid}: QCM image evidence mismatch")
                    answers=item.get("correct"); options=item.get("options")
                    rationales=item.get("optionRationales")
                    if (item.get("format")!="QCM" or
                        not isinstance(options,list) or len(options)!=5 or
                        len(set(options))!=5 or any(not x for x in options) or
                        not isinstance(rationales,list) or len(rationales)!=5 or
                        any(not x for x in rationales) or not isinstance(answers,list) or
                        not answers or len(set(answers))!=len(answers) or
                        any(not isinstance(x,int) or not 0<=x<=4 for x in answers)):
                        raise ValueError(f"{rid}: invalid A–E content")
                else:
                    if (item.get("sourceImageSha256")!=sha or
                        not item.get("studyCardStatus","").startswith("APPROVED") or
                        not item.get("question") or not item.get("answer")):
                        raise ValueError(f"{rid}: flashcard evidence mismatch")
                findings.append({"kind":kind,"id":rid,"course":cid,"page":page,"sha256":sha})
    for cid,guide in before["courseGuides"].items():
        nextguide=after["courseGuides"].get(cid)
        if nextguide is None:
            raise ValueError(f"Missing original guide {cid}")
        if nextguide!=guide:
            bs=guide.get("sections",[])
            ns=nextguide.get("sections",[])
            if ns[:len(bs)]!=bs or len(ns)<=len(bs):
                raise ValueError(f"{cid}: existing academic sections modified or removed")
            for sec in ns[len(bs):]:
                for item in sec.get("items",[]):
                    page=item.get("page")
                    if (item.get("sourceEvidence")!="REVIEWED_ORIGINAL_FC_IMAGE" or
                        not isinstance(page,int) or not 1<=page<=len(after["coursePages"][cid])):
                        raise ValueError(f"{cid}: unverified supplementary fact")
    return findings

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--before",required=True)
    p.add_argument("--candidate",required=True)
    p.add_argument("--source-apk",required=True)
    a=p.parse_args()
    try:
        before=json.loads(Path(a.before).read_text(encoding="utf-8"))
        candidate=json.loads(Path(a.candidate).read_text(encoding="utf-8"))
        evidence=inspect(before,candidate,a.source_apk)
        tally={"questions":sum(x["kind"]=="questions" for x in evidence),
               "flashcards":sum(x["kind"]=="flashcards" for x in evidence)}
        print(json.dumps({"passed":True,"tally":tally,"verifiedRecords":evidence,
                          "academicExhaustivenessCertified":False},ensure_ascii=False))
        return 0
    except (ValueError,OSError,KeyError,TypeError,zipfile.BadZipFile) as ex:
        print(json.dumps({"passed":False,"error":str(ex)},ensure_ascii=False))
        return 2
if __name__=="__main__":sys.exit(main())
