#!/usr/bin/env python3
"""Read-only release safety audit. Structural validity is NOT editorial verification."""
import argparse,collections,datetime,json,pathlib,sys,hashlib

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("corpus",type=pathlib.Path)
    parser.add_argument("--signoffs",type=pathlib.Path,help="manually approved per-course evidence registry")
    parser.add_argument("--report",type=pathlib.Path)
    parser.add_argument("--strict",action="store_true",help="fail if any course, question, map or flashcard lacks expert approval")
    a=parser.parse_args()
    d=json.loads(a.corpus.read_text(encoding="utf-8-sig"))
    signoffs=json.loads(a.signoffs.read_text(encoding="utf-8-sig")) if a.signoffs and a.signoffs.exists() else {}
    chapters=d.get("chapters",[]);ids={c["id"] for c in chapters};qs=d.get("questions",[]);cards=d.get("flashcards",[])
    guides=d.get("courseGuides",{});maps=d.get("mindMaps",{});pages=d.get("coursePages",{})
    structural=[];editorial=[]
    if len(ids)!=len(chapters):structural.append("DUPLICATE_COURSE_IDS")
    for kind,items in (("question",qs),("flashcard",cards)):
        used=set()
        for pos,item in enumerate(items):
            uid=str(item.get("id",""))
            if not uid or uid in used:structural.append(f"{kind}:{pos}:DUPLICATE_OR_MISSING_ID")
            used.add(uid)
            course=item.get("chapterId")
            if course not in ids:structural.append(f"{kind}:{uid}:UNKNOWN_COURSE")
            for key in (["stem"] if kind=="question" else ["question","answer"]):
                if not str(item.get(key,"")).strip():structural.append(f"{kind}:{uid}:EMPTY_{key}")
            sources=item.get("sourcePages",[])
            if not isinstance(sources,list):sources=[]
            if not sources and isinstance(item.get("source"),dict):
                one=item["source"].get("page")
                if isinstance(one,int):sources=[one]
            for page in sources:
                if not isinstance(page,int) or page<1 or (pages.get(course) and page>len(pages[course])):
                    structural.append(f"{kind}:{uid}:INVALID_SOURCE_PAGE:{page}")
    # A guide, QCM, flashcard or mindmap being present is NOT evidence it has been reviewed.
    states={}
    for course in chapters:
        cid=course["id"];record=signoffs.get(cid,{})
        sections=guides.get(cid,{}).get("sections",[])
        item_count=sum(len(s.get("items",[])) for s in sections)
        has_pages=bool(pages.get(cid))
        status={
            "course_id":cid,"subject":course["subjectId"],"title":course["title"],
            "source_pages_present":len(pages.get(cid,[])),"guide_section_count":len(sections),
            "guide_fact_count":item_count,"map_registered":cid in maps,
            "question_count":sum(x.get("chapterId")==cid for x in qs),
            "flashcard_count":sum(x.get("chapterId")==cid for x in cards),
            "guide_coverage_status":guides.get(cid,{}).get("coverageStatus","UNSPECIFIED"),
            "editorial_approved":False,"missing_gates":[]
        }
        if not has_pages:status["missing_gates"].append("SOURCE_PAGES_NOT_BUNDLED")
        if not sections:status["missing_gates"].append("GUIDE_ABSENT")
        if cid not in maps:status["missing_gates"].append("MINDMAP_ABSENT")
        for gate in ("source_full_coverage","exam_fidelity","flashcards_quality","mindmap_quality","page_by_page_editorial"):
            evidence=record.get(gate,{})
            # Self-declared approvals without hash or reviewer trace cannot open the gate.
            if evidence.get("result")!="APPROVED" or not evidence.get("reviewed_at") or not evidence.get("evidence_sha256"):
                status["missing_gates"].append(gate.upper()+"_UNVERIFIED")
        status["editorial_approved"]=not status["missing_gates"]
        if not status["editorial_approved"]:editorial.append(cid)
        states[cid]=status
    summary={
        "audited_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "corpus_sha256":hashlib.sha256(a.corpus.read_bytes()).hexdigest(),
        "course_count":len(chapters),"question_count":len(qs),"flashcard_count":len(cards),
        "courses_with_guides":sum(bool(guides.get(cid,{}).get("sections")) for cid in ids),
        "courses_with_source_pages":sum(bool(pages.get(cid)) for cid in ids),
        "courses_editorially_approved":sum(s["editorial_approved"] for s in states.values()),
        "structural_errors":structural,
        "unverified_courses":editorial,
        "release_ready":not structural and not editorial,
        "explanation":"Syntactic/source-pointer checks do not prove factual accuracy or source completeness.",
        "courses":states
    }
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("courses",)},ensure_ascii=False,indent=2))
    if structural: return 2
    if a.strict and editorial:
        print("RELEASE_BLOCKED: editorial/source coverage is not verified.",file=sys.stderr)
        return 3
    return 0
if __name__=="__main__":sys.exit(main())
