

if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside = {
    make_toast_draggable: function(is_open, id) {
        if (id && is_open) {
            //console.log(JSON.stringify(id));
            if (id.constructor == Object) {

                id = JSON.stringify(sortObjectByKeys(id));
            }
            
            dragElement(document.getElementById(id));

            function sortObjectByKeys(obj) {
                return Object.keys(obj)
                    .sort()
                    .reduce((acc, key) => ({ ...acc, [key]: obj[key] }), {});
            }
            

            function dragElement(elmnt) {
                var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
                elmnt.children[0].onmousedown = dragMouseDown;

                function dragMouseDown(e) {
                    e = e || window.event;
                    e.preventDefault();
                    // get the mouse cursor position at startup:
                    pos3 = e.clientX;
                    pos4 = e.clientY;
                    document.onmouseup = closeDragElement;
                    // call a function whenever the cursor moves:
                    document.onmousemove = elementDrag;
                }

                function elementDrag(e) {
                    e = e || window.event;
                    e.preventDefault();
                    // calculate the new cursor position:
                    pos1 = pos3 - e.clientX;
                    pos2 = pos4 - e.clientY;
                    //console.log(elmnt.style.width);

                    pos3 = e.clientX;
                    pos4 = e.clientY;
                    // set the element's new position:
                    elmnt.style.top = Math.min(Math.max((elmnt.offsetTop - pos2),0), window.innerHeight-100) + "px";
                    elmnt.style.left = Math.min(Math.max((elmnt.offsetLeft - pos1),0),window.innerWidth-100) + "px";
                }

                function closeDragElement() {
                    // stop moving when mouse button is released:
                    document.onmouseup = null;
                    document.onmousemove = null;
                }
            }
        }
        return window.dash_clientside.no_update;
    }
}