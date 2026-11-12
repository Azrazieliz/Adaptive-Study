#!/usr/bin/env python3
"""Populate reviewed FC facts and flashcards without recreating existing courses.

Checks original image bytes against the installed-v3.36.9 source APK, stable
chapter identity, source-page numbers, duplicate facts and existing records.
Creates a *new* candidate and an audit report; never edits the base, APK,
historical study progress, or a previously created candidate.
Image checksum is provenance, not by itself proof of scientific correctness.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from apply_incremental_study_patch import apply, FORMAT

SCHEMA="FC_SOURCE_REVIEWED_POPULATION_V1"

def norm(value: str) -> str:
    return re.sub(r"\W+"," ",value.casefold()).strip()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",required=True)
    ap.add_argument("--source-apk",required=True)
    ap.add_argument("--review",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--report",required=True)
    args=ap.parse_args()
    try:
        base_path=Path(args.base); out=Path(args.output); report_path=Path(args.report)
        if out.exists() or report_path.exists() or out.resolve()==base_path.resolve():
            raise ValueError("Refusing to overwrite source, candidate or audit")
        base_bytes=base_path.read_bytes();base=json.loads(base_bytes)
        source_hash=hashlib.sha256(base_bytes).hexdigest()
        review=json.loads(Path(args.review).read_text(encoding="utf-8"))
        if review.get("schema")!=SCHEMA or review.get("base_sha256")!=source_hash:
            raise ValueError("Source-version guard or review schema mismatch")
        edited=review.get("courses",{})
        if not isinstance(edited,dict) or not edited:
            raise ValueError("No approved course edits")
        actual_courses={c["id"]:c for c in base["chapters"]}
        changes={};manifest=[]
        known_card_ids={c["id"] for c in base["flashcards"]}
        with zipfile.ZipFile(args.source_apk) as z:
            for cid,block in edited.items():
                if cid not in actual_courses:
                    raise ValueError(f"{cid}: not a genuine course")
                page_list=base["coursePages"].get(cid)
                if not page_list:raise ValueError(f"{cid}: no original pages")
                oldguide=base["courseGuides"].get(cid)
                if not isinstance(oldguide,dict):raise ValueError(f"{cid}: no original guide")
                newguide=json.loads(json.dumps(oldguide,ensure_ascii=False))
                if not isinstance(block.get("reviewedPages"),list) or not block["reviewedPages"]:
                    raise ValueError(f"{cid}: no source-image-reviewed pages")
                existing={(norm(s.get("title","")),norm(i.get("label","")),norm(i.get("value","")))
                          for s in newguide.get("sections",[]) for i in s.get("items",[])}
                additions=[];cards=[]
                for entry in block["reviewedPages"]:
                    page=entry.get("page")
                    if not isinstance(page,int) or isinstance(page,bool) or not 1<=page<=len(page_list):
                        raise ValueError(f"{cid}: invalid page number")
                    original=page_list[page-1]
                    if entry.get("sourceImage")!=original:
                        raise ValueError(f"{cid}: page path not an exact FC registration")
                    try:raw=z.read("assets/www/"+original)
                    except KeyError as ex:raise ValueError(f"{cid}: original image missing") from ex
                    digest=hashlib.sha256(raw).hexdigest()
                    if entry.get("sourceImageSha256")!=digest:
                        raise ValueError(f"{cid}: original-image digest mismatch")
                    sections=entry.get("sections")
                    if not isinstance(sections,list) or not sections:
                        raise ValueError(f"{cid}: no authored source-linked section")
                    for s in sections:
                        title=s.get("title","")
                        if not 6<=len(title)<=130:raise ValueError(f"{cid}: bad section title")
                        items=s.get("items")
                        if not isinstance(items,list) or not 2<=len(items)<=18:
                            raise ValueError(f"{cid}: expected 2–18 genuinely separate facts")
                        approved=[]
                        for item in items:
                            label=item.get("label","");value=item.get("value","")
                            if not 3<=len(label)<=115 or not 10<=len(value)<=500:
                                raise ValueError(f"{cid}: empty/long source fact")
                            key=(norm(title),norm(label),norm(value))
                            if key in existing:raise ValueError(f"{cid}: duplicated academic fact")
                            existing.add(key)
                            approved.append({"label":label,"value":value,"page":page,
                                             "priority":item.get("priority",2),
                                             "sourceEvidence":"ORIGINAL_FC_IMAGE_REVIEWED_20261112"})
                        additions.append({"title":title,"type":"table","sourcePages":[page],"items":approved,
                                          "editorialStatus":"PARTIAL_PAGE_VERIFIED_NOT_FULL_COURSE"})
                    proposed=entry.get("flashcards",[])
                    if not isinstance(proposed,list) or len(proposed)>15:
                        raise ValueError(f"{cid}: excessive/invalid question entries")
                    for i,card in enumerate(proposed):
                        q=card.get("question","");a=card.get("answer","")
                        if not 8<=len(q)<=220 or not 6<=len(a)<=330:
                            raise ValueError(f"{cid}: flashcard content invalid")
                        rid=f"source26:{cid}:p{page}:{i+1:02}"
                        if rid in known_card_ids:raise ValueError(f"{cid}: duplicate flashcard ID")
                        known_card_ids.add(rid)
                        cards.append({"id":rid,"chapterId":cid,"subjectId":actual_courses[cid]["subjectId"],
                                      "question":q,"answer":a,"page":page,"priority":card.get("priority",2),
                                      "studyCardStatus":"APPROVED_ORIGINAL_FC_IMAGE_REVIEW_20261112",
                                      "sourceImageSha256":digest})
                    manifest.append({"courseId":cid,"sourcePage":page,"sourceImage":original,
                                     "imageSHA256":digest,"facts":sum(len(x["items"]) for x in sections),
                                     "flashcards":len(proposed)})
                newguide["sections"].extend(additions)
                newguide["incrementalSourceReview20261112"]={
                    "addedSections":len(additions),"scope":"PARTIAL_SOURCE_PAGE_COVERAGE_ONLY",
                    "pages":[x["page"] for x in block["reviewedPages"]]}
                changes[cid]={"courseGuides":newguide}
                if cards:changes[cid]["flashcards"]=cards
        candidate,audit=apply(base,{"format":FORMAT,"courses":changes},set(changes))
        if not audit["approved"]:raise ValueError("Incremental structural gate failed")
        output_json=json.dumps(candidate,ensure_ascii=False,separators=(",",":"))
        report={"ok":True,"baseSHA256":source_hash,"courses":sorted(changes),
                "sourcePageEvidence":manifest,"factsAdded":sum(x["facts"] for x in manifest),
                "flashcardsAdded":sum(x["flashcards"] for x in manifest),
                "originalQuestionsPreserved":candidate["questions"]==base["questions"],
                "existingFlashcardsPreserved":all(x in candidate["flashcards"] for x in base["flashcards"]),
                "allOriginalCoursesPreserved":candidate["chapters"]==base["chapters"],
                "fullAcademicCertification":False,"installedAPKChanged":False,
                "structuralGate":audit}
        out.parent.mkdir(parents=True,exist_ok=True);report_path.parent.mkdir(parents=True,exist_ok=True)
        with out.open("x",encoding="utf-8") as f:f.write(output_json)
        with report_path.open("x",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2)
        print(json.dumps(report,ensure_ascii=True))
        return 0
    except (OSError,KeyError,TypeError,ValueError,zipfile.BadZipFile) as ex:
        print(json.dumps({"ok":False,"error":str(ex)},ensure_ascii=True));return 2
if __name__=="__main__":sys.exit(main())
