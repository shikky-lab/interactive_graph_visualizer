var w = 1000;
var h = 1000;
var v_x = 500
var v_y = 500
var v_default_width = v_width = 1000
var v_default_height = v_height = 1000

var nodes;
var links;
d3.json("symple_graph.json", function (graph) {
    //console.log(graph);   
    nodes = graph.nodes;
    links = graph.links;
    draw(graph);
});

function draw(graph) {
    var svg = d3.select("body")
        .append("svg")
        .attr({ width: w, height: h })
        //.attr("viewBox", "" + v_x + " " + v_y + " " + v_width + " " + v_height);

    var g = svg.append('g');
    g.append("rect")//rectをグループ内に入れないとズームが効かない?
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("fill", "gray")
        .attr("opacity",0.3);

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

    var zoom = d3.behavior.zoom()
        //.translate([0, 0])
        //.scale(1)
        //.scaleExtent([1, 8])
        .scaleExtent([0.1, 10])
        //.size([w,h])
        .on("zoom", zoomed);

    g.call(zoom); // delete this line to disable free zooming
        //.call(zoom.event);

    force.start(); //force レイアウトの計算を開始
    for (var i = 500; i > 0; --i) force.tick(); //ワンステップ進める

    var link = g.selectAll("line")
                     .data(links)
                     .enter()
                     .append("line")
                     .style({
                         stroke: "#ccc",
                         "stroke-width": 1
                     })
                    .attr("transform", function(d) { return "translate(" + d + ")"; })
                    .attr({
                        "x1": function (d) { return d.source.x },
                        "y1": function (d) { return d.source.y },
                        "x2": function (d) { return d.target.x },
                        "y2": function (d) { return d.target.y },
                    });
    var node = g.selectAll("circle")
				  .data(nodes)
				  .enter()
				  .append("circle")
                    .attr("transform", function(d) { return "translate(" + d + ")"; })
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

    //force.stop(); //force レイアウトの計算を終了

    //force.on("tick", function() {
    //    link.attr({x1: function(d) { return d.source.x; },
    //        y1: function(d) { return d.source.y; },
    //        x2: function(d) { return d.target.x; },
    //        y2: function(d) { return d.target.y; }});
    //    node.attr({cx: function(d) { return d.x; },
    //        cy: function(d) { return d.y; }});
    //});


    function zoomed() 
    {
      //svg.style("stroke-width", 1.5 / d3.event.scale + "px");
        g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
        var befere_vbox_width, before_vbox_height, d_x, d_y;

        //befere_v_width = v_width
        //  before_v_height = v_height
        //  v_width = v_default_width * d3.event.scale
        //  v_height = v_default_height * d3.event.scale
        //  d_x = (befere_v_width - v_width) / 2
        //  d_y = (before_v_height - v_height) / 2
        //  v_x += d_x
        //  v_y += d_y
        //  return svg.attr("viewBox", "" + v_x + " " + v_y + " " + v_width + " " + v_height);
    }
}

