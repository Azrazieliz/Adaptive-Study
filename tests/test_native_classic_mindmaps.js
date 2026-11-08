"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");

const file=path.join(__dirname,"..","native-android","app","src","main","java","com","azrazieliz","adaptivestudy","MainActivity.java");
const src=fs.readFileSync(file,"utf8");
const section=(start,end)=>{
  const a=src.indexOf(start),b=src.indexOf(end,a+start.length);
  assert(a>=0&&b>a,"Missing expected native method boundaries: "+start);
  return src.slice(a,b);
};

const map=section("private void showConceptMap(){","private void showStructuredMap(){");
assert.match(map,/drawImage\(s\(mind,"path"\)\)/,"Original course mind-map image must open directly");
assert.match(map,/drawImage\(s\(page,"path"\)\)/,"Original detail images must be retained");
assert.match(map,/subMaps/,"Preserve existing map-to-detail routing");
assert.doesNotMatch(map,/showAuthoredMap|openFullMapReader|MapRail|fitToPage|fitToWidth|zoomBy/,"No replacement maps or extra zoom panels");

const image=section("private void drawImageInto(LinearLayout target,String path){","private void drawPdf(String path){");
assert.match(image,/new ZoomImageView\(this\)/);
assert.doesNotMatch(image,/imageHeight|displayWidth|Math\.min\(dp\(850\)/,"Do not force map preview aspect/height");

const zoom=section("private final class ZoomImageView", "private final class androidxPlaceholderImageView");
assert.match(zoom,/ScaleGestureDetector/,"Pinch-to-zoom handler must remain");
assert.match(zoom,/detector\.onTouchEvent\(ev\)/,"Pinch detector must receive touch events");
assert.match(zoom,/matrix\.postTranslate\(dx,dy\)/,"Drag panning must remain");
console.log("Classic native mind-map source regression checks passed");
