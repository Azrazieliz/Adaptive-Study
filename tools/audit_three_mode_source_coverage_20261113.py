#!/usr/bin/env python3
"""Source-linked study-mode and visual coverage audit. Never certifies unread FC pages."""
from __future__ import annotations
import argparse,collections,hashlib,json,pathlib,re,sys
INACTIVE=frozenset(("histo_embryo","biocell_cytosq","biocell_mec_integrine","biocell_dev","biocell_cycle"))
RECOVER=frozenset(("biocell_noyau","bio_proteines","bio_biomol","chim_atoliais","chim_protons","phys_energie_elec","phys_fluides"))

def j(path):
    p=pathlib.Path(path)
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--data",required=True)
    a.add_argument("--visual",required=True)
    a.add_argument("--repairs",required=True)
    a.add_argument("--expert",required=True)
    a.add_argument("--comprehension",required=True)
    a.add_argument("--output",required=True)
    args=a.parse_args()
    corpus=j(args.data); visual=j(args.visual); repairs=j(args.repairs); expert=j(args.expert); comprehension=j(args.comprehension)
    chapters=[c for c in corpus.get("chapters",[]) if c["id"] not in INACTIVE]
    assert len(chapters)==76,len(chapters)
    assert RECOVER.issubset({c["id"] for c in chapters})
    visual_by_course=visual.get("courses",{})
    repaired=repairs.get("courses",{})
    expert_by_course=expert.get("courses",{})
    comprehension_by_course=comprehension.get("chapters",{})
    guides=corpus.get("courseGuides",{})
    pages=corpus.get("coursePages",{})
    rows=[]
    for course in chapters:
        cid=course["id"]; source=pages.get(cid,[])
        verified=set()
        boards=visual_by_course.get(cid,[])
        for board in boards:
            if (board.get("reviewStatus")=="PAGE_IMAGE_REVIEWED" and
                isinstance(board.get("reviewEvidence"),dict)):
                for n in board.get("sourcePages",[]):
                    if isinstance(n,int) and 0<n<=len(source):verified.add(n)
        guide=guides.get(cid,{})
        source_repair=repaired.get(cid,{})
        structured=guide.get("sections",[])
        comprehension_entry=comprehension_by_course.get(cid,{})
        expert_entry=expert_by_course.get(cid,{})
        mode_status={
            "essentiel":"SOURCE_STRUCTURED_UNCERTIFIED" if structured or source_repair.get("essential") else "MISSING",
            "complet":"SOURCE_STRUCTURED_UNCERTIFIED" if structured or source_repair.get("complete") else "MISSING",
            "comprendre":"SOURCE_STRUCTURED_UNCERTIFIED" if comprehension_entry or expert_entry or source_repair.get("understand") else "MISSING"
        }
        if cid in RECOVER:mode_status={k:"BLOCKED_WRONG_FC_PAGE_OWNERSHIP" for k in mode_status}
        rows.append({
            "courseId":cid, "title":course.get("title"),"subjectId":course.get("subjectId"),
            "sourcePagesReferenced":len(source), "distinctPageReferences":len(set(source)),
            "visuallyReviewedPageNumbers":sorted(verified),
            "visuallyReviewedPageCount":len(verified),
            "sourcePagesNotVerifiedByVisualBoard":max(0,len(source)-len(verified)),
            "reviewedVisualBoardCount":sum(b.get("reviewStatus")=="PAGE_IMAGE_REVIEWED" for b in boards),
            "flowDiagramCount":sum(b.get("layout")=="flow" and b.get("reviewStatus")=="PAGE_IMAGE_REVIEWED" for b in boards),
            "mechanismPilotReviewedPages":[6,14] if cid=="histo_nerveux" else [],
            "modeState":mode_status, "independentFcIdentityResolved":cid not in RECOVER,
            "editorialCertification":"UNVERIFIED"
        })
    summary={
        "activeOriginalCoursesPreserved":len(chapters),
        "fabricatedInactiveRegistryEntriesKeptArchived":len(INACTIVE),
        "originalCourseIdsRequiringSourceRecovery":len(RECOVER),
        "verifiedVisualBoards":sum(x["reviewedVisualBoardCount"] for x in rows),
        "coursesWithSourceVerifiedVisualBoards":sum(bool(x["reviewedVisualBoardCount"]) for x in rows),
        "totalSourcePageReferences":sum(x["sourcePagesReferenced"] for x in rows),
        "visuallyReviewedUniqueCoursePages":sum(x["visuallyReviewedPageCount"] for x in rows),
        "unreviewedSourcePageReferences":sum(x["sourcePagesNotVerifiedByVisualBoard"] for x in rows),
        "understandAllPagesCertified":False,
        "notes":"Reviewed visuals are only one category of evidence. Indexed text, PDF presence and prior synthetic prose do not certify complete pages. Counts are conservative."
    }
    result={"schema":"ASTERION_THREE_MODE_SOURCE_COVERAGE_V1","summary":summary,"courses":rows}
    dst=pathlib.Path(args.output);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"output":str(dst),"summary":summary,
                      "neural":next(x for x in rows if x["courseId"]=="histo_nerveux")},ensure_ascii=True))
if __name__=="__main__":sys.exit(main())
