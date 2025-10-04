let sidebarFrame = null;

function toggleSidebar() {
    if (!sidebarFrame) {
        sidebarFrame = document.createElement('iframe');
        sidebarFrame.id = 'ff-sidebar-iframe';
        sidebarFrame.src = chrome.runtime.getURL('sidebar.html');
        document.body.appendChild(sidebarFrame);
        
        setTimeout(() => {
            sidebarFrame.classList.add('visible');
        }, 10);

    } else {
        sidebarFrame.classList.toggle('visible');
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.command === "toggleSidebar") {
        toggleSidebar();
        sendResponse({status: "done"});
    }
    return true;
});