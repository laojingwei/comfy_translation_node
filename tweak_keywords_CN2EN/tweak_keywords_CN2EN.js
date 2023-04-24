import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
	name: "xww.Tweak Keywords CN2EN",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "Tweak Keywords CN2EN") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated?.apply(this, arguments);

				const w = ComfyWidgets["STRING"](this, "text", ["STRING", { multiline: true }], app).widget;

				return r;
			};
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				this.widgets[0].value = message.text;

				if (this.size[1] < 180) {
					this.setSize([this.size[0], 180]);
				}
			};
		}
	},
});