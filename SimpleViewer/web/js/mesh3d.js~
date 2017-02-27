function getRandomIntInclusive(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min + 1)) + min;
}
if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

function FFBOMesh3D(div_id, data, func) {

	this.div_id = div_id;
	this.func = func;

	this.container = document.getElementById( div_id );
	var height = this.container.clientHeight;
	var width = this.container.clientWidth;

	this.fov = 20;

	this.camera = new THREE.PerspectiveCamera( this.fov, width / height, 0.1, 20000 );
	this.camera.position.z = 1800;
	this.camera.position.y = 100;

	this.renderer = new THREE.WebGLRenderer();
	this.renderer.setPixelRatio( window.devicePixelRatio );
	this.renderer.setSize( width, height );
	this.container.appendChild(this.renderer.domElement);

	this.scene = new THREE.Scene();
	this.scene.add( this.camera );

	this.meshGroup = new THREE.Object3D(); // for raycaster detection

	this.currentIntersected;

	this.mouse = new THREE.Vector2(-100000,-100000);

	this.timeliner = {};
	this.timelinerJson = {};

	this.isAnim = false;

	this.controls = new THREE.TrackballControls(this.camera, this.renderer.domElement);
	this.controls.rotateSpeed = 2.0;
	this.controls.zoomSpeed = 1.0;
	this.controls.panSpeed = 2.0;
	this.controls.staticMoving = true;
	this.controls.dynamicDampingFactor = 0.3;
	this.controls.addEventListener('change', this.render.bind(this));

	this.frontlight = new THREE.DirectionalLight();
	this.frontlight.position.set( 0, 0, 1 );
	this.scene.add( this.frontlight );

	this.backlight = new THREE.DirectionalLight();
	this.backlight.position.set( 0, 0, -5000 );
	this.scene.add( this.backlight );
	/*
	 * create color map
	 */
	this.maxColorNum = 1747591;
	this.lut = new THREE.Lut( 'rainbow', this.maxColorNum );
	this.lut.setMax( 1 );
	this.lut.setMin( 0 );

	this.loadingManager = new THREE.LoadingManager();
	this.scene.add( this.meshGroup );

	this.raycaster = new THREE.Raycaster();
	this.raycaster.linePrecision = 3;

	this.container.addEventListener( 'click', this.onDocumentMouseClick.bind(this), false );

	this.container.addEventListener( 'dblclick', this.onDocumentMouseDBLClick.bind(this), false );

	this.container.addEventListener( 'mousemove', this.onDocumentMouseMove.bind(this), false );

	this.container.addEventListener( 'mouseleave', this.onDocumentMouseLeave.bind(this), false );

	this.container.addEventListener( 'resize', this.onWindowResize.bind(this), false );

	this.meshDict = {};
	this.meshNum = 0;
	this.globalCenter = {'x':0.0, 'y':0.0, 'z':0.0};
	if ( data != undefined && Object.keys(data).length > 0)
		this.addJson( data );

	this.toolTipPos = new THREE.Vector2();
	this.createToolTip();

	this.isHighlight = false;
	this.highlightedObj = null;

	//this.initTimeliner();
	this.animate();
	this.pinned = new Set();

	this.dispatch = {
		'click': undefined,
		'dblclick': undefined
	}

};
FFBOMesh3D.prototype.reset = function() {
	for (var key in this.meshDict) {
		var meshobj = this.meshDict[key].object;
		for (var i = 0; i < meshobj.children.length; i++ ) {
			meshobj.children[i].geometry.dispose();
			meshobj.children[i].material.dispose();
		}
	}
	this.scene.remove( this.meshGroup );
	this.meshGroup = new THREE.Object3D();
	this.scene.add( this.meshGroup );
	this.meshDict = {};
	this.meshNum = 0;
	this.isHighlight = false;
	this.highlightedObj = null;
	this.pinned.clear()
	this.globalCenter = {'x':0.0, 'y':0.0, 'z':0.0};
}
FFBOMesh3D.prototype.addJson = function(json, visibility) {
	if (json === undefined) {
	    console.log( 'mesh json is undefined' );
	    return;
	}
	if (visibility === undefined)
		visibility = true;
    if ('type' in json && json['type']=='morphology_json'){
	    //json = JSON.parse(json['ffbo_json']);
	    json = json['ffbo_json']; 
	    for ( var key in json ) {
		if (key in this.meshDict ) {
		    console.log( 'mesh object already exists... skip rendering...' )
		    continue;
		}
		this.meshDict[key] = json[key];
		this.meshNum += 1;

		var id = this.meshNum;
		if ( !('highlight' in this.meshDict[key]) )
		    this.meshDict[key]['highlight'] = true;

		if ( !('color' in this.meshDict[key]) )
		    this.meshDict[key]['color'] = this.lut.getColor( getRandomIntInclusive(1, this.maxColorNum)/this.maxColorNum );

		if ('name' in this.meshDict[key])
		    this.meshDict[key]['label'] = this.meshDict[key]['name'];
		if ( !('label' in this.meshDict[key]) )
		    this.meshDict[key]['label'] = key;

		this.loadMorphJSONCallBack(key, visibility).bind(this)();
		
	    }
	}
        else{
	
	    for ( var key in json ) {
		if (key in this.meshDict ) {
		    console.log( 'mesh object already exists... skip rendering...' )
		    continue;
		}
		this.meshDict[key] = json[key];
		this.meshNum += 1;

		if ( ('dataStr' in this.meshDict[key]) && ('filename' in this.meshDict[key]) ) {
		    console.log( 'mesh object has both data string and filename... should only have one... skip rendering' );
		    continue;
		}
		var id = this.meshNum;
		if ( !('color' in this.meshDict[key]) )
		    this.meshDict[key]['color'] = this.lut.getColor( getRandomIntInclusive(1, this.maxColorNum)/this.maxColorNum );

		if ( !('highlight' in this.meshDict[key]) )
		    this.meshDict[key]['highlight'] = true;

		if ( !('label' in this.meshDict[key]) )
		    this.meshDict[key]['label'] = key;

		/* read mesh */
		if ( 'filename' in this.meshDict[key] ) {
		    this.meshDict[key]['filetype'] = this.meshDict[key].filename.split('.').pop();
		    var loader = new THREE.XHRLoader( this.loadingManager );
		    if (this.meshDict[key]['filetype']  == "json")
			loader.load(this.meshDict[key].filename, this.loadMeshCallBack(key, visibility).bind(this));
		    else if (this.meshDict[key]['filetype'] == "swc" )
			loader.load(this.meshDict[key].filename, this.loadSWCCallBack(key, visibility).bind(this));
		    else {
			console.log( 'mesh object has unrecognized data format... skip rendering' );
			continue;
			}
		} else if ( 'dataStr' in this.meshDict[key] ) {
		    if (this.meshDict[key]['filetype']  == "json")
			this.loadMeshCallBack(key, visibility).bind(this)(this.meshDict[key]['dataStr']);
		    else if (this.meshDict[key]['filetype'] == "swc" )
			this.loadSWCCallBack(key, visibility).bind(this)(this.meshDict[key]['dataStr']);
		    else {
			console.log( 'mesh object has unrecognized data format... skip rendering' );
			continue;
		    }
		} else {
		    console.log( 'mesh object has neither filename nor data string... skip rendering' );
		    continue;
		}
	    }
	}
}
FFBOMesh3D.prototype.animate = function() {

	requestAnimationFrame( this.animate.bind(this) );

	this.controls.update(); // required if controls.enableDamping = true, or if controls.autoRotate = true

	this.render();
}
FFBOMesh3D.prototype.loadMeshCallBack = function(key, visibility) {
	return function (jsonString) {

		var json = JSON.parse(jsonString);
		var color = this.meshDict[key]['color'];
		var geometry  = new THREE.Geometry();
		var vtx = json['vertices'];
		var idx = json['faces'];
		var center = {'x':0.0, 'y':0.0, 'z':0.0};
		var len = vtx.length / 3;
	        for (var j = 0; j < len; j++) {
			var x = parseFloat(vtx[3*j+0]);
			var y = parseFloat(vtx[3*j+1]);
			var z = parseFloat(vtx[3*j+2]);
			geometry.vertices.push(
				new THREE.Vector3(x,y,z)
			);
			center.x += x/len;
			center.y += y/len;
			center.z += z/len;
		}
		for (var j = 0; j < idx.length/3; j++) {
			geometry.faces.push(
				new THREE.Face3(
					parseInt(idx[3*j+0]),
					parseInt(idx[3*j+1]),
					parseInt(idx[3*j+2])
				)
			);
		}

		geometry.computeFaceNormals();
		geometry.computeVertexNormals();

		var materials = [
			//new THREE.MeshPhongMaterial( { color: color, shading: THREE.FlatShading, shininess: 0, transparent: true } ),
			new THREE.MeshLambertMaterial( { color: color, transparent: true, side: 2, shading: THREE.FlatShading} ),
			new THREE.MeshBasicMaterial( { color: color, wireframe: true, transparent: true} )
		];
		var group = THREE.SceneUtils.createMultiMaterialObject( geometry, materials );
		group.visible = visibility;

		this._registerGroup(key, group, center);
	};

};
FFBOMesh3D.prototype.loadSWCCallBack = function(key, visibility) {
	return function(swcString) {
		/*
		 * process string
		 */
		swcString = swcString.replace(/\r\n/g, "\n");
		var swcLine = swcString.split("\n");
		var len = swcLine.length;
		var swcObj = {};

		swcLine.forEach(function (e) {
			var seg = e.split(' ');
			if (seg.length == 7) {
				swcObj[parseInt(seg[0])] = {
					'type'   : parseInt  (seg[1]),
					'x'      : parseFloat(seg[2]),
					'y'      : parseFloat(seg[3]),
					'z'      : parseFloat(seg[4]),
					'radius' : parseFloat(seg[5]),
					'parent' : parseInt  (seg[6]),
				};
			}
		});

		var color = this.meshDict[key]['color'];
		var geometry  = new THREE.Geometry();
		var center = {'x':0.0, 'y':0.0, 'z':0.0};

		for (var idx in swcObj ) {
			if (swcObj[idx].parent != -1) {
				var c = swcObj[idx];
				var p = swcObj[swcObj[idx].parent];
				geometry.vertices.push(new THREE.Vector3(c.x,c.y,c.z));
				geometry.vertices.push(new THREE.Vector3(p.x,p.y,p.z));
				geometry.colors.push(color);
				geometry.colors.push(color);
				center.x += c.x/len;
				center.y += c.y/len;
				center.z += c.z/len;
			}
		}
		var material = new THREE.LineBasicMaterial({ vertexColors: THREE.VertexColors, transparent: true, color: color });
		var group = new THREE.Object3D();
		group.add(new THREE.LineSegments(geometry, material, THREE.LineSegments));
		group.visible = visibility;

		this._registerGroup(key, group, center);

	};
};

FFBOMesh3D.prototype.loadMorphJSONCallBack = function(key, visibility) {
    return function() {
	/*
	 * process string
	 */
	var swcObj = {};
	var len = this.meshDict[key]['sample'].length;
	for (var j = 0; j < len; j++) {
	    swcObj[parseInt(this.meshDict[key]['sample'][j])] = {
		'type'   : parseInt  (this.meshDict[key]['identifier'][j]),
		'x'      : parseFloat(this.meshDict[key]['x'][j]),
		'y'      : parseFloat(this.meshDict[key]['y'][j]),
		'z'      : parseFloat(this.meshDict[key]['z'][j]),
		'radius' : parseFloat(this.meshDict[key]['r'][j]),
		'parent' : parseInt  (this.meshDict[key]['parent'][j]),
	    };
	}
	
	var color = this.meshDict[key]['color'];
	var geometry  = new THREE.Geometry();
	var center = {'x':0.0, 'y':0.0, 'z':0.0};
	var sphereGeometry = undefined;
	
	for (var idx in swcObj ) {
	    var c = swcObj[idx];
	    if (c.parent != -1) {
		var p = swcObj[c.parent];
		geometry.vertices.push(new THREE.Vector3(c.x,c.y,c.z));
		geometry.vertices.push(new THREE.Vector3(p.x,p.y,p.z));
		geometry.colors.push(color);
		geometry.colors.push(color);
		center.x += c.x/len;
		center.y += c.y/len;
		center.z += c.z/len;
	    }
	    if (c.type == 1) {
		sphereGeometry = new THREE.SphereGeometry( 3, 8, 8 );
		sphereGeometry.translate( c.x, c.y, c.z );
	    }
	}
	var material = new THREE.LineBasicMaterial({ vertexColors: THREE.VertexColors, transparent: true, color: color });
	var group = new THREE.Object3D();
	group.add(new THREE.LineSegments(geometry, material, THREE.LineSegments));
	if ( sphereGeometry !== undefined ) {
		var sphereMaterial = new THREE.MeshPhongMaterial( {color: color, transparent: true} );
		group.add(new THREE.Mesh( sphereGeometry, sphereMaterial));
	}
	group.visible = visibility;
	
	this._registerGroup(key, group, center);
	
    };
};

FFBOMesh3D.prototype._registerGroup = function(key, group, center) {

	/* create label for tooltip if not provided */
	group.name = this.meshDict[key].label;
	group.uid = key;

	this.meshDict[key]['object']  = group;
	this.meshDict[key]['pinned']  = false;

	/* reset the position of the entire scene */
	this.meshGroup.translateX(this.globalCenter.x/this.meshNum);
	this.meshGroup.translateY(this.globalCenter.y/this.meshNum);
	this.meshGroup.translateZ(this.globalCenter.z/this.meshNum);

	this.meshGroup.add( group );

	/* compute the new global center, and tcenter the the entire scene */
	this.globalCenter.x = this.globalCenter.x*(this.meshNum-1)/this.meshNum + center.x/this.meshNum;
	this.globalCenter.y = this.globalCenter.y*(this.meshNum-1)/this.meshNum + center.y/this.meshNum;
	this.globalCenter.z = this.globalCenter.z*(this.meshNum-1)/this.meshNum + center.z/this.meshNum;
	this.meshGroup.translateX(-this.globalCenter.x/this.meshNum);
	this.meshGroup.translateY(-this.globalCenter.y/this.meshNum);
	this.meshGroup.translateZ(-this.globalCenter.z/this.meshNum);
}
FFBOMesh3D.prototype.initTimeliner = function() {
	this.timelinerJson = {};
	for (var key in this.meshDict)
		this.timelinerJson[key] = 0;
	this.timeliner = new Timeliner(this.timelinerJson);
	/*
	 * load a dummy animation script
	 */
	var dummyAnimJson = {
		"version":"1.2.0",
		"modified":"Mon Dec 08 2014 10:41:11 GMT+0800 (SGT)",
		"title":"Untitled",
		"ui": {"totalTime": 1},
		"layers":[]
	}
	for (var key in this.meshDict) {
		var dict = {"name": key, "values": [{"time":0.01, "value":0.55}], "_value":0, "_color":"#6ee167"};
		dummyAnimJson["layers"].push(dict);
	}
	this.timeliner.load(dummyAnimJson);
}

FFBOMesh3D.prototype.onDocumentMouseClick = function( event ) {
	event.preventDefault();

	if (this.dispatch['click'] != undefined && this.currentIntersected != undefined ) {
		var x = this.currentIntersected;
		if (this.meshDict[x.uid]['highlight'])
			this.dispatch['click']([x.name, x.uid]);
	}
}

FFBOMesh3D.prototype.onDocumentMouseDBLClick = function( event ) {
	event.preventDefault();

	if (this.currentIntersected != undefined ) {
		var x = this.currentIntersected;
		if (!this.meshDict[x.uid]['highlight'])
			return;
		this.togglePin(x.uid);
		if (this.dispatch['dblclick'] !== undefined )
			this.dispatch['dblclick'](x.uid, x.name, this.meshDict[x.uid]['pinned']);
	}
}

FFBOMesh3D.prototype.onDocumentMouseMove = function( event ) {
	event.preventDefault();

	var rect = this.container.getBoundingClientRect();

	this.toolTipPos.x = event.clientX + 10;
	this.toolTipPos.y = event.clientY + 10;

	this.mouse.x = ( (event.clientX - rect.left) / this.container.clientWidth ) * 2 - 1;
	this.mouse.y = - ( (event.clientY - rect.top) / this.container.clientHeight ) * 2 + 1;

}

FFBOMesh3D.prototype.onDocumentMouseLeave = function( event ) {
	event.preventDefault();

	this.hide3dToolTip();
	this.resume();

}
//
FFBOMesh3D.prototype.onWindowResize = function() {

	var height = this.container.clientHeight;
	var width = this.container.clientWidth;

	this.camera.aspect = width / height;
	this.camera.updateProjectionMatrix();

	this.renderer.setSize( width, height );

	this.controls.handleResize();

	this.render();
}


FFBOMesh3D.prototype.render = function() {

	if (this.isAnim) {
		for (var key in this.meshDict) {
			if (this.meshDict[key].object != undefined) {
				this.meshDict[key].object.children[0].material.opacity = this.timelinerJson[key];
				if (this.meshDict[key].object.children.length > 1 )
					this.meshDict[key].object.children[1].material.opacity = 0.1;
			}
		}
	} else if (this.isHighlight) {

	} else {
		for (var key in this.meshDict) {
			if (this.meshDict[key].object != undefined) {
				var x = new Date().getTime();
				if ( !this.meshDict[key]['highlight'] ) {
					this.meshDict[key].object.children[0].material.opacity = 0.15 + 0.15*Math.sin(x * .0005);
					//this.meshDict[key].object.children[1].material.opacity = 0.15 - 0.15*Math.sin(x * .0005);
					this.meshDict[key].object.children[1].material.opacity = 0.1;
					//this.meshDict[key].object.children[0].material.opacity = 0.2;
				} else {
					//this.meshDict[key].object.children[0].material.opacity = 0.3 - 0.3*Math.sin(x * .0005);
					//this.meshDict[key].object.children[0].material.opacity = 0.8;
				}
			}
		}
	}

	/*
	 * show label of mesh object when it intersects with cursor
	 */
	this.raycaster.setFromCamera( this.mouse, this.camera );

	var intersects = this.raycaster.intersectObjects( this.meshGroup.children, true);
	if ( intersects.length > 0 ) {
		this.currentIntersected = intersects[0].object.parent;
		/* find first object that can be highlighted (skip  mesh) */
		for (var i = 1; i < intersects.length; i++ ) {
			var x = intersects[i].object.parent;
			if (this.meshDict[x.uid]['highlight']) {
				this.currentIntersected = x;
				break;
			}
		}
		if ( this.currentIntersected !== undefined ) {
			this.show3dToolTip(this.currentIntersected.name);
			this.highlight(this.currentIntersected.uid);
		}
	} else {
		if ( this.currentIntersected !== undefined ) {
			this.hide3dToolTip();
			this.resume();
		}
		this.currentIntersected = undefined;
	}

	this.renderer.render( this.scene, this.camera );
}

FFBOMesh3D.prototype.showAll = function() {
	for (var key in this.meshDict)
		this.meshDict[key].object.visible = true;
};

FFBOMesh3D.prototype.hideAll = function() {
	for (var key in this.meshDict)
		if (!this.meshDict[key]['pinned'])
			this.meshDict[key].object.visible = false;
};

FFBOMesh3D.prototype.show = function(key) {
	if (key in this.meshDict)
		this.meshDict[key].object.visible = true;
	if (this.highlightedObj !== null && this.highlightedObj[0] == key)
		this.highlightedObj[1] = true;
}

FFBOMesh3D.prototype.hide = function(key) {
	if (key in this.meshDict)
		this.meshDict[key].object.visible = false;
	if (this.highlightedObj !== null && this.highlightedObj[0] == key)
		this.highlightedObj[1] = false;
}

FFBOMesh3D.prototype.toggleVis = function(key) {
	if (key in this.meshDict)
		this.meshDict[key].object.visible = !this.meshDict[key].object.visible;
}

FFBOMesh3D.prototype.openTimeliner = function() {
	this.isAnim = true;
	// TODO
	$("#anim-ctrl-pane").show();
	$("#ghostpane").show();
}

FFBOMesh3D.prototype.closeTimeliner = function() {
	this.isAnim = false;
	this.timeliner.close();
	// TODO
	$("#anim-ctrl-pane").hide();
	$("#ghostpane").hide();
}

FFBOMesh3D.prototype.highlight = function(d) {

	if (!(d in this.meshDict) || !(this.meshDict[d]['highlight']))
		return;
	if (this.highlightedObj !== null  && d !== this.highlightedObj[0])
		this.resume();

	this.highlightedObj = [d, this.meshDict[d].object.visible];
	for (var key in this.meshDict) {
		if (this.meshDict[key]['pinned'])
			continue;
		// TODO:
		var val = (this.meshDict[key]['highlight']) ? 0.2 : 0.05;
		if (this.meshDict[key]['pinned'])
			val = 0.4;
		for (i in this.meshDict[key].object.children)
			this.meshDict[key].object.children[i].material.opacity = val;
	}
	for (i in this.meshDict[d].object.children)
		this.meshDict[d].object.children[i].material.opacity = 1;
	this.meshDict[d].object.visible = true;
	this.isHighlight = true;
}

FFBOMesh3D.prototype.resume = function() {

	if (this.highlightedObj === null)
		return;
	var d = this.highlightedObj[0];
	var x = this.meshDict[d].object.children;
	var val;
	if (!this.meshDict[d]['pinned']) {
		this.meshDict[d].object.visible = this.highlightedObj[1];
		this.highlightedObj = null;
		val = 0.2;
	} else
		val = 0.6;
	for (i in x)
		x[i].material.opacity = val;
	if (this.pinned.size === 0)
		this.resetOpacity();
	this.isHighlight = false;
}


FFBOMesh3D.prototype.resetOpacity = function() {
	var val = 0.8;
	//if (this.pinnedNum > 0)
	//	val = 0.2;
	//reset
	for (var key in this.meshDict) {
		if (!this.meshDict[key]['highlight'])
			continue;
		//var op = (this.meshDict[key]['pinned']) ? 0.6 : val;

		for (i in this.meshDict[key].object.children)
			this.meshDict[key].object.children[i].material.opacity = val;
	}
}

FFBOMesh3D.prototype.togglePin = function( id ) {

	this.meshDict[id]['pinned'] = !this.meshDict[id]['pinned'];
	if (this.meshDict[id]['pinned']) {
		this.pinned.add(id)
	} else {
		this.pinned.delete(id)
	}

	if (this.pinned.size == 0)
		this.resetOpacity();
	else {
		var val = (this.meshDict[id]['pinned']) ? 0.8 : 0.2;
		for (i in this.meshDict[id].object.children)
			this.meshDict[id].object.children[i].material.opacity = val;
	}
}

FFBOMesh3D.prototype.unpinAll = function() {

	for (let key of this.pinned.values())
		this.meshDict[key]['pinned'] = false;
	this.pinned.clear();
	this.resetOpacity();
}

FFBOMesh3D.prototype.loadAnimJson = function(json) {
	this.timeliner.load(json);
}

FFBOMesh3D.prototype.createToolTip = function() {
	this.toolTipDiv = document.createElement('div');
	this.toolTipDiv.id = 'toolTip';
	this.toolTipDiv.style.cssText = 'position: fixed; text-align: center; width: 100px; height: 50px; padding: 2px; font: 12px arial; z-index: 999; background: lightsteelblue; border: 0px; border-radius: 8px; pointer-events: none; opacity: 0.0;';
	this.toolTipDiv.style.transition = "opacity 0.5s";
	document.body.appendChild(this.toolTipDiv);
}

FFBOMesh3D.prototype.show3dToolTip = function (d) {
	this.toolTipDiv.style.opacity = .9;
	this.toolTipDiv.style.left = this.toolTipPos.x + "px";
	this.toolTipDiv.style.top = this.toolTipPos.y + "px";
	this.toolTipDiv.innerHTML = "<h5>" + d + "</h5>";
}

FFBOMesh3D.prototype.hide3dToolTip = function () {
	this.toolTipDiv.style.opacity = 0.0;
}
