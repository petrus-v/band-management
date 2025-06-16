(function () {
  htmx.onLoad(function (content) {
    var sortables = content.querySelectorAll(".sortable");
    for (var i = 0; i < sortables.length; i++) {
      var sortable = sortables[i];
      var sortableInstance = new Sortable(sortable, {
        multiDrag: true,
        // handle: "sortable-handler",
        animation: 150,
        selectedClass: 'sortable-selected', // The class applied to the selected items
        fallbackTolerance: 3, // So that we can select items on mobile
        ghostClass: 'sortable-ghost-background',  // The class applied to the ghost element
        swapThreshold: 0.90,
      });

    }
  });
})();