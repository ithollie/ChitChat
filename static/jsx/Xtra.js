/*

Created: 2018-07-10
Modified: N/A
Purpose: Extra functions, but they're Xtra cause we are cool.
(Actually these helper functions might become general enough to be re-usable in a personal library)

*/
/*global localStorage*/
/*global L*/
/*global m*/
/*global v*/
/*global c*/

c.not = (x) => !x;
c.log = (...args) => console.log.apply(null,args);
///////////////| music player methods |///////////////////////
c.setMusicSource = (source) => v.player.src = source;
c.play = () => v.player.play();
c.pause = () => v.player.pause();
c.mute = (boolean )=> v.player.muted = boolean;
c.getTime = () => v.player.currentTime;
c.setTime = (time) => v.player.currentTime = time; //in milliseconds
c.setVolume = (volume) => v.player.volume = volume;
c.getVolume = () => v.player.volume;
c.getDuration = () => v.player.duration;
c.durationOk = () => c.not( m.badDurationStates.includes(c.getDuration()) );  
c.getPaused = () => v.player.paused;
////////////////////////////////
c.shuffle = (boolean)=>{
	//	m.currentSong
	//	m.currentSongFilenamesArray
	//  v.songSelector
	if(boolean){
		m.currentSongFilenamesArray = L.scrambleThis(m.currentSongFilenamesArray);
		const index = m.currentSongFilenamesArray.indexOf(m.currentSong);
		//alert(index)
		c.fillSelector(m.currentSongFilenamesArray);
		v.songSelector.selectedIndex = index;
	}
	else{
		m.currentSongFilenamesArray.sort();
		const index = m.currentSongFilenamesArray.indexOf(m.currentSong);
		//alert(index)
		c.fillSelector(m.currentSongFilenamesArray);
		v.songSelector.selectedIndex = index;		
	}
	
};
////////////////////////////////
c.initializeAudio = function(){
	c.showPlayPauseIn();
	setTimeout(()=>{
		c.showPlayPauseOut();
	}, 500);
};
////////////////////////////////
c.updateProgressBar = function (){
	if(c.durationOk){
		m.musicFraction = c.getTime() / c.getDuration();
		v.progressBar.styles(`width: ${100 * m.musicFraction}%`);
	}

};
//////////////////////////////
c.updateVolumeBar = ()=>{
	m.volumeColor =  120 * (1 - m.volumeFraction);	//between 120 and 0 degrees hsl ( green -> red )
	//change the player's volume:
	c.setVolume(m.volumeFraction);
	//cosmetic change:
	v.volumeBar
		.styles
			(`height: ${100 * m.volumeFraction}%`)
			(`background-image: linear-gradient(90deg, white, ${m.volumeColor}, 50%, 50%, gray)`);
};
//////////////////////////////
c.showPlayPauseIn = function(){
	v.playPause
		.styles
			(`box-shadow: inset 8px 8px 25px black`)
			(`background-image: url(images/pause.png)`);
			//(`background-color: rgba(0,0,0,0.3)`)
};
c.showPlayPauseOut = function(){
	v.playPause
		.styles
			(`box-shadow: 1px 1px 1px black`)
			(`background-image: url(images/play.png)`)
			(`background-color: transparent`);
};
//////////////////////////////
c.queueCurrentSong = ()=>{
	c.setMusicSource( `${m.songsBaseUrl}${m.currentSong}.mp3` );
	v.songTitle.innerText = m.currentSong;
	c.setTime(0);
	m.songFraction = 0;
	c.showPlayPauseOut();	
};
//////////////////////////////
c.getFullListSabbaKilam = ()=>{
	const postman = new XMLHttpRequest();
	//m.songsBaseUrl = `https://SabbaKilam.github.io/music/`
	postman.open( 'GET', `${m.songsBaseUrl}list.json` );
	postman.send();
	////////////////////
	postman.onload = ()=>{
		m.currentSongFilenamesArray = ( Object.keys(JSON.parse(postman.responseText)) ).sort();
		c.fillSelector(m.currentSongFilenamesArray);
    //let a random appear (not always song 0):
    const randomIndex =  Math.floor(m.currentSongFilenamesArray.length * Math.random());
    v.songSelector.selectedIndex = randomIndex;    
		m.currentSong = v.songSelector.options[randomIndex].innerText;
		c.queueCurrentSong();		
	};
};
/////////////////////
c.fillSelector = (textArray)=>{
  v.songSelector.innerHTML = ``;
	for (let song of textArray){
		let optionElement = document.createElement('option');
		optionElement.innerText = song;
		v.songSelector.appendChild(optionElement);
	}
	//
};
/////////////////////
c.reloadApp = ()=>{
	const reload = confirm(`     OK to Reload App?\n     (if not, CANCEL)`);
	if(reload){
		window.location.href = (`${window.location.href}?${Date.now()}`);		
	}
};
///////////////////
c.changeNextPictureDemo =()=>{
  //change picture for demo only:
  m.fingerSlidingPicture = false;  
  m.albumPicturesArray.unshift(m.albumPicturesArray.pop());
  v.currentAlbumCover
    .styles
      (`opacity: 0`)
      (`visibility: hidden`)  
      (`left: -200%`);
      //(`background-image: url(${m.albumPicturesArray[0]})`);
      c.showPicture(v.currentAlbumCover, m.defaultPictureUrl);
      c.showNewPicture(v.currentAlbumCover);
   setTimeout(()=>{
    v.currentAlbumCover
      .styles
        (`left: 200%`);
  },300);
  setTimeout(()=>{
    v.currentAlbumCover
      .styles
        (`opacity: 1`)
        (`visibility: visible`)     
        (`left: 0`);
  },450); 	
	
}
/////////////////////
c.showPicture = (destination, source)=>{
	destination.styles(`background-image: url(${source})`)
	
}
////////////////////
c.showNewPicture = (destination)=>{
  const songKey = m.currentSong
  
  if(localStorage.getItem(songKey)){
    let storedData = localStorage.getItem(songKey)
    c.showPicture(destination, storedData)
    console.log(`Using locally stored image for ${songKey}`)
    return
  }
  
	let songUrl = `${m.songsBaseUrl}${songKey}.mp3`
  var jsmediatags = window.jsmediatags; //localize jsmediatags
  if(!jsmediatags){  
    console.log("Can't find the 'jsmediatags' object.");
    console.log("Try https://github.com/aadsm/jsmediatags/tree/master/dist/jsmediatags.min.js");
    console.log("... or https://cdnjs.cloudflare.com/ajax/libs/jsmediatags/3.9.0/jsmediatags.js");
    return;
  }
  jsmediatags.read(songUrl, {
    onSuccess: (tag) => {
      let tags = tag.tags;
      let image = tags.picture;
      if (image) {
        const asciiData = image.data.reduce((string, datum) => string += String.fromCharCode(datum), '');
        const base64String = "data:" + image.format + ";base64," + window.btoa(asciiData);
        m.pictureData = base64String;
        if(localStorage.getItem(songKey)){
          let storedData = localStorage.getItem(songKey)
          if(m.currentSong === songKey){
            c.showPicture(destination, storedData)
          }
        }
        else{
          if(m.currentSong === songKey){
            c.showPicture(destination, m.pictureData)            
          }
          localStorage.setItem(songKey, m.pictureData)
        }
      }
      else{
        console.log(`There is NO picture for ${songKey}.`);
        //c.showPicture(destination, m.defaultPictureUrl)  
      }
    },
    onError: (error) => {
      //c.showPicture(destination, m.defaultPictureUrl)      
      //console.log(error);
      return;
    }  
 }) 	

}
////////////////////
c.getSongList = async ()=>{
  let fetch = window.fetch;
	//console.log(`Should be getting song list.`)
	const textPromise = await fetch(`php/getSongList.php`)
	const longString = await textPromise.text()
	const songListArray = longString.split(`\n`)

	//remove the final newline and then sort
	songListArray.pop()
	songListArray.sort()	
	
	//slice off the ".mp3"  extention from each filename
	songListArray.forEach((m,i,a)=>{
		a[i] = m.slice(0,-4)
	})
	//console.log(songListArray)
	m.currentSongFilenamesArray = songListArray
	// shuffle or alphabetize
	m.shuffle
	  ? m.currentSongFilenamesArray = L.scrambleThis(m.currentSongFilenamesArray)
	  : m.currentSongFilenamesArray.sort()
	  
	c.fillSelector(m.currentSongFilenamesArray)
	
	////| If it's the first load, choose a random song |//////
	if(m.firstLoad){
	  m.firstLoad = false
    //let a random song appear (not always song 0):
    const randomIndex =  Math.floor(m.currentSongFilenamesArray.length * Math.random());
    v.songSelector.selectedIndex = randomIndex;    
		m.currentSong = v.songSelector.options[randomIndex].innerText;
		c.queueCurrentSong();		 
    c.showNewPicture(v.currentAlbumCover)
	}
	/////| If it's not the first load, point song selector to the current song |//////
	else{
    const index = m.currentSongFilenamesArray.indexOf(m.currentSong)
    m.selectedIndex = index
    v.songSelector.selectedIndex = index
	}
}


///////////////////////////////////////////////
//////////| for remote picture data |//////////
///////////////////////////////////////////////
/*
	let songUrl = `${m.songsBaseUrl}${songKey}.mp3`
  new Promise((resolve, reject)=>{ 
    var ajax = new XMLHttpRequest();
    ajax.responseType = 'blob';
    ajax.open('GET', songUrl);
    ajax.send();
    //////////////////////////
    ajax.onload = function(){
      if(ajax.status === 200){
        resolve(ajax.response);
      }
      else{
        reject("nay :(");
      }
    };
    ajax.onerror = function(){
        reject("Trouble connecting to server");
    }
  })
  .then(   response => new Blob( [response],{type: "audio/*"} )   )
  .then( musicContent => {
    //console.log(musicContent)
    //attempt to show image
    var jsmediatags = window.jsmediatags; //cargo-culted line from source documentation
    if(!jsmediatags){  
      console.log("Can't find the 'jsmediatags' object.");
      console.log("Try https://github.com/aadsm/jsmediatags/tree/master/dist/jsmediatags.min.js");
      console.log("... or https://cdnjs.cloudflare.com/ajax/libs/jsmediatags/3.9.0/jsmediatags.js");
      return;
    }
    jsmediatags.read(musicContent, {
      onSuccess: (tag) => {
        var tags = tag.tags;
        //========================//
        let image = tags.picture;
        if (image) {  
        	console.log(`There is a picture: `, tags);
          const asciiData = image.data.reduce((string, datum) => string += String.fromCharCode(datum), '');
          const base64String = "data:" + image.format + ";base64," + window.btoa(asciiData);
          m.pictureData = base64String;
          if(localStorage.getItem(songKey)){
            let storedData = localStorage.getItem(songKey)
            c.showPicture(destination, storedData)
          }
          else{
            c.showPicture(v.currentAlbumCover, m.pictureData)
            localStorage.setItem(songKey, m.pictureData)
          } //
        }
        else{
          //c.showPicture(destination, m.defaultPictureUrl)  
        }
      },
      onError: (error) => {
        //c.showPicture(destination, m.defaultPictureUrl)      
        //console.log(error);
        return;
      }  
   })      
  })////| end of 2nd then |////
  .catch()
  */