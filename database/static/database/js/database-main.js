function exportSequences (gene_name, clade_id, matches) {
    console.log (gene_name+" +"+clade_id+"("+matches.length+")");
    console.log (matches)
    
    if (matches.length == 0) {
        r = confirm("We could not identify the pattern for "+clade_id+" in "+gene_name+". We can't add this clade automatically!");   
    } else {
       console.log ("add clade");
       $.ajax({   
       url : "{% url 'add_clade_to_gene' %}"     , // the endpoint
       type : "POST", // http method
       data : { gene_name : gene_name, 
               clade_id : clade_id,
               matches : JSON.stringify(matches)},
       success : function(json) {
           console.log("success"); // another sanity check
           console.log(json); // log the returned json to the console
           html_list = ""
           for (key in json['matches']) {
                html_list += "<li><span onclick='addClade(\""+json['gene_name']+"\", \""+key+"\","+json['matches'][key].length+")'>"+key+":"+json['matches'][key].length;
           } 
           $("#id-clade").html(html_list);
            
          },
       
       });  
   }
}


function addClade (gene_name, clade_id, matches) {
    console.log (gene_name+" +"+clade_id+"("+matches.length+")");
    console.log (matches)
    
    if (matches.length == 0) {
        r = confirm("We could not identify the pattern for "+clade_id+" in "+gene_name+". We can't add this clade automatically!");   
    } else {
       console.log ("add clade");
       $.ajax({   
       url : add_clade_to_gene_url  , // the endpoint
       type : "POST", // http method
       data : { gene_name : gene_name, 
               clade_id : clade_id,
               matches : JSON.stringify(matches)},
       success : function(json) {
           console.log("success"); // another sanity check
           console.log(json); // log the returned json to the console
           html_list = ""
           for (key in json['matches']) {
                html_list += "<li><span onclick='addClade(\""+json['gene_name']+"\", \""+key+"\","+json['matches'][key].length+")'>"+key+":"+json['matches'][key].length;
           } 
           $("#id-clade").html(html_list);
            
          },
       
       });  
   }
}


