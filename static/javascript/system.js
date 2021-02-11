
const  m =  {};//Model
const  v =  {};//view
const  c =  {};//Controller
const  mainPage = {};//main page
const arrays = {};

c.initialize  =  function(eventObject){
  v.u    = c.id(`ut`);
  v.e    = c.id(`big`);
  v.ie   = c.id(`newi`);
  v.iei  = c.id(`wow`);
  v.hed  = c.id(`header`);
  v.infor = c.id(`infor`);
  v.branchesOfgovernment = c.id(`big`);

  v.hed.style.backgroundImage  = c.new();
  v.e.style.backgroundImage  = c.header();
  v.branchesOfgovernment.addEventListener(`mouseenter`, c.branches);
  //v.branchesOfgovernment.children[0].children.addEventListener(`click`, c.reacte);
  v.infor.style.visibility = "hidden"

  c.number = 0;
  c.youtube = {"Executive":"https://www.youtube.com/embed/FgJr15lfIys",
        "Justic":"https://www.youtube.com/embed/FgJr15lfIys",
        "Congress":"https://www.youtube.com/embed/FgJr15lfIys"
  }
}
mainPage.main =  function(){
  mainPage.reacte();
}

mainPage.reacte =  function(eventObject){
  const  gov =  v.branchesOfgovernment.children[0].children.length;
  for(var i = 0;i< gov;i++){
        v.branchesOfgovernment.children[0].children[i].addEventListener(`click`, function(eventObject){
        c.number +=1;
        for(var key in c.youtube){
          if(key ==  eventObject.target.attributes[0].nodeValue){
            if(c.number == 1){
              console.log(v.infor)
              v.infor.style.visibility="visible";
            }else{
              if(c.number == 2){
                console.log(v.infor)
                v.infor.style.visibility="hidden";
                c.number = 0;
              }
            }
        }
      }
    });
  }
}
mainPage.hiddeClicked =  function(eventObject){
  const  gov =  v.branchesOfgovernment.children[0].children.length;
  for(var i = 0;i< gov;i++){
        v.branchesOfgovernment.children[0].children[i].addEventListener(`click`, function(eventObject){
        for(var key in c.youtube){
          if(key ==  eventObject.target.attributes[0].nodeValue){
            console.log(v.infor)
            v.infor.style.visibility="hidden";
            c.number +=1;
        }
      }
    });
  }
}
mainPage.EachClicked =  function(eventObject){
  alert(eventObject.target);
}

c.header = function(){
  //return "url('images/p.jpg')";
}
c.new  = function(){
  //return "url('images/DC.jpg')";
}

c.newi = function(){
  return "url('static/images/Shades-of-Blue-Color-Names4.jpg')";

}

c.gift =  function(){
  return "url('/static/images/Shades-of-Blue-Color-Names4.jpg')";
}

c.id = function(viewString){
  return document.getElementById(viewString);
}
