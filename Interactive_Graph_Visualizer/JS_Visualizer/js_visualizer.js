var w = 400;
var h = 400;
var svg = d3.select("body").append("svg").attr({ width: w, height: h });

var nodes;
var links;
d3.json("graph.json", function (graph) {
    //console.log(graph);   
    nodes = graph.nodes;
    links = graph.links;
    draw(graph);
});

var zoom = d3.behavior.zoom()
    .translate([0, 0])
    .scale(1)
    .scaleExtent([1, 8])
    .on("zoom", zoomed);

//var g = svg.append("g");

svg
    .call(zoom) // delete this line to disable free zooming
    .call(zoom.event);

function zoomed() 
{
  svg.style("stroke-width", 1.5 / d3.event.scale + "px");
  svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

function draw(graph) {
    var force = d3.layout.force()
				 .nodes(nodes)
				 .links(links)
				 .size([w, h])
				 .linkStrength(0.1)
				 .friction(0.9)
				 .distance(200)
				 .charge(-300)
				//.chargeDistance(1000000)
				 .gravity(0.1)
				 .theta(0.8)
				 .alpha(0.1)
				 .start();

    force.start(); //force レイアウトの計算を開始
    for (var i = 500; i > 0; --i) force.tick(); //ワンステップ進める

    var link = svg.selectAll("line")
                     .data(links)
                     .enter()
                     .append("line")
                     .style({
                         stroke: "#ccc",
                         "stroke-width": 1
                     })
    .attr({
        "x1": function (d) { return d.source.x },
        "y1": function (d) { return d.source.y },
        "x2": function (d) { return d.target.x },
        "y2": function (d) { return d.target.y },
    });
    var node = svg.selectAll("circle")
				  .data(nodes)
				  .enter()
				  .append("circle")
				  .attr({
				      r: 20,
				      opacity: 0.5
				  })
				  .style({ fill: "red" })
                .attr({
                    class: "node",
                    "r": 8,
                    "fill": "black",
                    "cx": function (d) { return d.x },
                    "cy": function (d) { return d.y }
                })
				  .call(force.drag);

    force.stop(); //force レイアウトの計算を終了

    //zoomFit()

    force.on("tick", function() {
      link.attr({x1: function(d) { return d.source.x; },
                 y1: function(d) { return d.source.y; },
                 x2: function(d) { return d.target.x; },
                 y2: function(d) { return d.target.y; }});
      node.attr({cx: function(d) { return d.x; },
                 cy: function(d) { return d.y; }});
    });

    //// zoomビヘイビアの設定
    //var zoom = d3.behavior.zoom()
    //  .scaleExtent([0.1, 10])
    //  .on("zoom", function(){
    //    container.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    //  });
     
    //// SVG を zoom ビヘイビアに渡す
    //var svg = d3.select("#MyGraph")
    //  .attr("width", w)
    //  .attr("height", h)
    //  .append("g")
    //  .attr("transform", "translate(0,0)")
    //  .call(zoom);
     
    //var container = svg.append("g");
     
    //// pointer-events = all でマウスイベントをSVGの描画範囲全体で拾うよう設定
    //var rect = svg.append("rect")
    //  .attr("width", w)
    //  .attr("height", h)
    //  .style("fill", "none")
    //  .style("pointer-events", "all");

    //function zoomFit(transitionDuration) {
    //    var bounds = root.node().getBBox();
    //    var parent = root.node().parentElement;
    //    var fullWidth = parent.clientWidth || parent.parentNode.clientWidth,
    //        fullHeight = parent.clientHeight || parent.parentNode.clientHeight;
    //    var width = bounds.width,
    //        height = bounds.height;
    //    var midX = bounds.x + width / 2,
    //        midY = bounds.y + height / 2;
    //    if (width == 0 || height == 0) return; // nothing to fit
    //    var scale = 0.85 / Math.max(width / fullWidth, height / fullHeight);
    //    var translate = [fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY];

    //    console.trace("zoomFit", translate, scale);

    //    root
    //        .transition()
    //        .duration(transitionDuration || 0) // milliseconds
    //        .call(zoom.translate(translate).scale(scale).event);
    //}
}

