// constant variables used to draw svg proteins
const margin = {"top": 0, "right": 5, "bottom": 0, "left": 10};
const width = 800 - margin.left - margin.right;
const height = 60 - margin.top - margin.bottom;
const y_line = (height + margin.top + margin.bottom)/2;
const rect_height = 12;
const y_rect = y_line - rect_height/2;


d3.json("./data.json").then(function(families) {

    // initialize the page with the content of the 1st element of families 
    initPage(families[0]);

    // list all family names in the panel "List of protein families"
    // each element is a <div class="nav-famlist"> 
    var famList = d3.select("#nav-content").selectAll("div")
        .data(families)
        .enter().append("div")
            .attr("class", "nav-famlist")
            .style("display", "block")
            .style("text-align", "left")
            .text(function (d) {
                return d.name;
            })

    // add the class "fam-selected" to the first element of the class "nav-famlist"
    d3.select(".nav-famlist").classed("fam-selected", true);

    // change text size and style of nav-famlist elements when hovering over
    famList.on("mouseover", function () {
        d3.select(this)
            .style("cursor", "pointer")
            .style("font-size", "14px")
            .style("font-style", "italic")
    }) 

    // restaure text size and style of nav-famlist elements when mouse out
    famList.on("mouseout", function () {
        d3.select(this).style("color", "black")
            .style("font-size", "13px")
            .style("font-style", "normal")
    })

    // manage click event happening on nav-famlist elements
    famList.on("click", function() {
        // add fam-selected class to the element clicked only
        d3.selectAll(".fam-selected").classed("fam-selected", false);
        d3.select(this).classed("fam-selected", true)

        // write name of the family in rule definition header 
        d3.select("#rule-summary .subtitle-header span").select("text").remove()
        d3.select("#rule-summary .subtitle-header span")
        .text(this.__data__.name)

        // write name of the family in domain architecture header
        d3.select("#proteins-container .subtitle-header span").select("text").remove()
        d3.select("#proteins-container .subtitle-header span")
        .text(this.__data__.name)

        updateRuleSummary(this.__data__.rules);
        rmProteins();
        drawProteins(this.__data__.proteins);
        updateDetails(this.__data__.proteins[0]);

    })

    d3.selectAll(".infobox").on("click", function() {
        var infobox = this;
        var duration_time = 275;
        var grandParent = this.parentNode.parentNode

        var selected_fam = d3.select("#rule-summary .subtitle-header span").text()
        d3.selectAll(".infobox .sp-rulename")
            .text(selected_fam);

        d3.select(infobox).select(".infotext")
            .style("visibility", "visible")

        d3.select(".hiding-panel")
            .style("z-index", "2")
            .style("display", "initial")
            .transition().duration(duration_time)
                .style("opacity", "0.65")

        d3.select(grandParent)
            .style("z-index", "5")
            // .style("opacity", "1")
            .style("background-color", "white")
    
        if (d3.select(".hiding-panel").style("display") == "initial") {
            
            d3.select(".hiding-panel").on("click", function() {
                d3.select(grandParent)
                .style("z-index", "1")
                
                d3.select(".hiding-panel")
                    .transition().duration(duration_time)
                        .style("z-index", "-1")
                        .style("opacity", "0.0")

                d3.select(infobox).select(".infotext")
                .transition().duration(duration_time)
                    .style("visibility", "hidden");

                setTimeout(function () {
                    d3.select(".hiding-panel")
                        .style("display", "none");
                    }, duration_time);        
                })
            }
    })                
});


function initPage(data) {
    d3.selectAll(".sp-rulename")
        .text(data.name);

    updateRuleSummary(data.rules);
    updateDetails(data.proteins[0]);
    drawProteins(data.proteins);
}


function drawProteins(data) {
    var proteins = data
    var protein_length = proteins.map(function(d) {return +d.length;})

    var scale = d3.scaleLinear()
        .domain([0, d3.max(protein_length)])
        .range([0, width]);

    // proteins-draw is the container in which proteins are drawn
    var div = d3.select("#proteins-draw").selectAll("div")
                .data(proteins)
                .enter().append("div")
                    .attr("class", "protein")

    var subdiv = div.append("div")
        .attr("class", "protein-descr")
        .text(d => {
            return `${d.id} (${d.length} aa)`;
        })
        .style("font-weight", "bold")
        .style("border-bottom", "1px solid")

    d3.select(".protein-descr ").classed("selected", true);

    var svg = subdiv.append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)

    var g = svg.append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
                .attr("class", d => d.id)

    g.append("line")
        .attr("x1", scale(1))
        .attr("y1", y_line)
        .attr("x2", d => scale(+d.length))
        .attr("y2", y_line)
        .attr("stroke", "black")
        .attr("stroke-width", "2")

    var rect = g.selectAll("rect")
                .data(d => d.domains)
                .enter().append("rect")
                    .attr("x", d => scale(d.start))
                    .attr("y", y_rect)
                    .attr("height", rect_height)
                    .attr("width", d => scale(d.length))
                    .attr("fill", d => d.color)
                    .attr("stroke", "black")
                    .attr("stroke-width", "1.25")
                    .attr("fill-opacity", 0.85)
                    .attr("rx", "8")
                    .attr("ry", "8")
                    .attr("id", function(d) {
                        var end = d.start + d.length - 1;
                        return `rect_${d.name}_${d.start}-${end}`; 
                    })
                    .style("visibility", function(d) {
                        if (d.status) {
                            if (d.status === "unlikely") {
                                return "hidden";
                            } else {
                                return "visible";
                            }
                        } else {
                            return "visible";
                    }})        

    rect.append("title")
        .text(d => `${d.name} (${d.length} aa)`)

    subdiv.on("click", function() {
        d3.selectAll(".selected").classed("selected", false);
        d3.select(this).classed("selected", true);

        updateDetails(this.__data__);
    })
    
    rect.on("mouseenter", function(event, d) {
        d3.select(`#${d.name}-${d.start}`).selectAll("td")
            .style("border-color", "black")
            .style("border-width", "2px")
            .style("font-weight", "bold")
            .classed("rect-hovered", true)
        })

    rect.on("mouseleave", function(event, d) {   
        d3.select(`#${d.name}-${d.start}`).selectAll("td")
            .style("border-width", "1px")
            .style("font-weight", "normal")
            .classed("rect-hovered", false);
    })
}


function rmProteins() {
    d3.select("#proteins-draw").selectAll(".protein").remove()
}


function updateDetails(protein){
    var domNbMLA = d3.sum(protein.domains.map(function(d) {
        if (d.status === "likely") {
            return 1;
        }
        else { return 0; }
    }))

    d3.selectAll(".p-id").text(protein.id)
    d3.select("#p-length").text(`${protein.length} amino acids`)
    d3.select("#p-domainInArch").text(domNbMLA)
    
    d3.select("#p-totalDomain").text(`${protein.domains.length}`)


    d3.select("#detail-hmmdomtbl tbody").selectAll("tr").remove()
    var rows = d3.select("#detail-hmmdomtbl tbody").selectAll("tr")
        .data(protein.domains)
        .enter().append("tr")
            .attr("id", function(d) {return `${d.name}-${d.start}` })
            .attr("class", d => d.status)

    rows.append("td").text(function(d) {return d.name})
    rows.append("td").text( d => d.start)
    rows.append("td").text( d => (d.start+d.length-1))
    rows.append("td").text( d => d.cevalue)
    rows.append("td").text( d => d.ievalue)
    rows.append("td").text( d => d.score)
    rows.append("td").text( d => d.hmm_length)
    rows.append("td").text( d => d.hmm_start)
    rows.append("td").text( d => d.hmm_end)


    rows.on("mouseenter", function(event, d) {
        d3.select(this).selectAll("td")
            .style("border-color", "black")
            .style("border-width", "2px")
            .style("font-weight", "bold")
            .classed("rect-hovered", true)

        d3.select(`g.${protein.id}`).selectAll("rect")
            .attr("opacity", "0.175")

        d3.select(`g.${protein.id}`).select("line")
            .attr("opacity", "0.4")

        var end = d.start + d.length - 1;
        d3.select(`#rect_${d.name}_${d.start}-${end}`)
            .attr("stroke-width", "2")
            .attr("opacity", "0.985")
            .style("visibility", "visible")
    })

    rows.on("mouseout", function(event, d) {
        d3.select(this).selectAll("td")
        .style("border-width", "1px")
        .style("font-weight", "normal")
        .classed("rect-hovered", false);
        
        d3.select(`g.${protein.id}`).selectAll("rect")
            .attr("opacity", "1")
            .attr("fill-opacity", "0.85")

        d3.select(`g.${protein.id}`).select("line")
            .attr("opacity", "1")

        var end = d.start + d.length - 1;
        d3.select(`#rect_${d.name}_${d.start}-${end}`)
            .attr("stroke-width", "1.25")
            .style("visibility", function(d) {
                if (d.status) {
                    if (d.status === "unlikely") {
                        return "hidden";
                    } else {
                        return "visible";
                    }
                } else {
                    return "visible";
            }})
    })

}


function updateRuleSummary(rules) {
    d3.selectAll(".rule-table").selectAll("td").remove()

    d3.select(".rule-table .tr-name").selectAll("td")
        .data(rules.mandatories)
        .enter().append("td")
        .text(d => d.name)

    var legend = d3.select(".rule-table .tr-legend").selectAll("td")
    .data(rules.mandatories)
    .enter().append("td")

    legend.append("svg")
        .attr("width", 50)
        .attr("height", 20)
        .append("rect")
            .attr("x", 9)
            .attr("y", 4)
            .attr("height", "14")
            .attr("width", "40")
            .attr("fill", d => d.color)
            .attr("stroke", "black")
            .attr("fill-opacity", "0.85")
            .attr("rx", "8")
            .attr("ry", "8")

    d3.select(".rule-table .tr-cutoff").selectAll("td")
        .data(rules.mandatories)
        .enter().append("td")
        .text(d => d.evalue)

    if (rules.forbidden[0].name != "None") {
        d3.select('.rule-table.forbidden-list')
        .style("visibility", "visible")

        d3.select(".rule-table .tr-name-forb").selectAll("td")
        .data(rules.forbidden)
        .enter().append("td")
        .text(d => d.name)

        var legend = d3.select(".rule-table .tr-legend-forb").selectAll("td")
        .data(rules.forbidden)
        .enter().append("td")

        legend.append("svg")
            .attr("width", 50)
            .attr("height", 20)
            .append("rect")
                .attr("x", 9)
                .attr("y", 4)
                .attr("height", "14")
                .attr("width", "40")
                .attr("fill", d => d.color)
                .attr("stroke", "black")
                .attr("fill-opacity", "0.85")
                .attr("rx", "8")
                .attr("ry", "8")
    } else {
        d3.select('.rule-table.forbidden-list')
            .style("visibility", "hidden")
    }
}

