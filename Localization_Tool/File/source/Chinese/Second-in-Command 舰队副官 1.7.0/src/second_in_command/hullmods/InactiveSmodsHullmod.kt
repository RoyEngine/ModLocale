package second_in_command.hullmods

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.BaseHullMod
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc

class InactiveSmodsHullmod : BaseHullMod() {

    override fun shouldAddDescriptionToTooltip(hullSize: ShipAPI.HullSize?, ship: ShipAPI?, isForModSpec: Boolean): Boolean {
        return false
    }

    override fun addPostDescriptionSection(tooltip: TooltipMakerAPI?, hullSize: ShipAPI.HullSize?, ship: ShipAPI?, width: Float, isForModSpec: Boolean) {

        tooltip!!.addSpacer(10f)
        tooltip.addPara("具备 \"万里挑一\" 技能的执行军官未被指派，导致该舰船存在超出可用上限的 失效 S-插件}。 " +
                "重新指派一名具备该技能的军官以解锁船插。", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "万里挑一", "失效 S-插件")
        tooltip!!.addSpacer(10f)

        tooltip.addPara("失效船插：{" ,0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        var variant = ship!!.variant

        for (tag in ArrayList(variant.tags)) {
            if (tag.startsWith("sc_inactive_smods_")) {
                var hmodId = tag.replace("sc_inactive_smods_", "")

                var spec = Global.getSettings().getHullModSpec(hmodId)
                tooltip.addPara(" - ${spec.displayName}", 0f)

            }
        }
    }

}