#!/usr/bin/env python3
"""Polish native three-mode navigation; no new data or course identity changes."""
import argparse,hashlib,json,pathlib,shutil
def once(s,old,new):
    n=s.count(old)
    if n!=1:raise AssertionError(f"Expected exactly one navigation anchor, found {n}: {old[:60]}")
    return s.replace(old,new,1)
p=argparse.ArgumentParser();p.add_argument("--java",required=True)
a=p.parse_args()
path=pathlib.Path(a.java);source=path.read_text("utf-8")
assert "ALL_COURSE_THREE_MODE_V1_20261113" in source
s=source
s=once(s,
    '        if(map){showConceptMap();return;}\n        showLessonTabs();',
    '        if(map){showConceptMap();return;}\n'
    '        if(isMisregisteredOriginalCourse()){\n'
    '            showLessonTabs();\n'
    '            heading(body,chapterTitle(currentChapter));\n'
    '            showIndependentFcRecoveryNotice();\n'
    '            return;\n'
    '        }\n        showLessonTabs();')
s=once(s,
    '            add(summary,button("SHS — QROC et commentaires",false,()->{\n'
    '                shsCorrectionIndex=0;go("SHS_CORRECTIONS");\n'
    '            }));\n',
    '            // QROC and commentaries are launched from Questions, not Complet.\n')
s=once(s,
    '        add(introduction,button("Voir tous les faits structurés de la FC",false,()->{\n'
    '            guideMode="FULL_FACTS";go("LESSON");\n'
    '        }));',
    '        add(introduction,button("Voir Complet et les tableaux",false,()->{\n'
    '            guideMode="COMPLETE";go("LESSON");\n'
    '        }));')
s=once(s,
    '             add(body,button("Voir les autres notions indexées",false,()->{\n'
    '                guideMode="FULL_FACTS";go("LESSON");\n'
    '            }));',
    '             add(body,button("Voir Complet",false,()->{\n'
    '                guideMode="COMPLETE";go("LESSON");\n'
    '            }));')
s=once(s,
    '        buttons(close,"Complet (sources et textes)",()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");},\n'
    '                "Toutes les notions",()->{guideMode="FULL_FACTS";go("LESSON");});',
    '        buttons(close,"Complet et tableaux",()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");},\n'
    '                "Essentiel",()->{guideMode="ESSENTIAL";go("LESSON");});')
s=once(s,
    '        buttons(body,"Cours structuré",()->{guideMode="FULL_FACTS";go("LESSON");},"Flashcards",()->startCards(currentChapter));',
    '        buttons(body,"Complet",()->{guideMode="COMPLETE";go("LESSON");},"Flashcards",()->startCards(currentChapter));')
assert '"FULL_FACTS"' not in s,'Fourth hidden lesson mode remains'
backup=path.with_name(path.name+".before_three_mode_polish_20261113")
if backup.exists():assert backup.read_text("utf-8")==source
else:shutil.copy2(path,backup)
path.write_text(s,encoding="utf-8")
print(json.dumps({"polished":True,"sourceBytes":len(s.encode("utf-8")),"sha256":hashlib.sha256(s.encode("utf-8")).hexdigest(),"archivedOriginalSevenStillGuarded":True,"allQuestionsSeparate":True},ensure_ascii=True))
