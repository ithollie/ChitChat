
const v = {};
const m = {};
const c = {};

/////////////////////////////
c.initialize = function(eventObject) {
	v.play =  document.getElementById('playPause');
	v.e    =  document.getElementById('updates');
	v.play.addEventListener('click', c.play);
	
}

c.play =  function(eventObject){
	for(let  i = 0 ; i < v.e.childNodes[1].childNodes.length; i++){
		let g = v.e.addEventListener('click', function(eventObject){
			 console.log(eventObject);
		})   
	}
}
	
	