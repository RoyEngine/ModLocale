package second_in_command.skills.management

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.misc.levelBetween
import second_in_command.specs.SCBaseSkillPlugin

class InGoodHands : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "所有指派有军官的舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("指派有军官的舰船的部署点降低", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 依据军官等级，舰船的部署点降低 0%%-15%% ", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "0%", "15%")
        tooltip.addPara("   - 军官等级达到 5 时达到最大效果", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "5")
        tooltip.addPara("   - 部署点数最多减少 10 点", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "10")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        var captain = stats!!.fleetMember?.captain ?: return

        if (captain.isDefault /*|| captain.isAICore*/) return

        var level = captain.stats.level.toFloat()
        var scale = level.levelBetween(0f, 5f)
        var reductionPercent = 0.15f * scale

        val baseCost = stats.suppliesToRecover.baseValue
        val reduction = Math.min(10f, baseCost * reductionPercent)

        stats.dynamic.getMod(Stats.DEPLOYMENT_POINTS_MOD).modifyFlat(id, (-reduction).toFloat())

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }


}