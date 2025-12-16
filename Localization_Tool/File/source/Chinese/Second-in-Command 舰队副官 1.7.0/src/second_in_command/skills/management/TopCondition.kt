package second_in_command.skills.management

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class TopCondition : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {
        tooltip.addPara("+30 秒 峰值时间", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 指派有军官的舰船效果{翻倍", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "翻倍")
    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        var ppt = 30f

        var captain = stats!!.fleetMember?.captain
        if (captain != null && !captain.isDefault /*&& !captain.isAICore*/) {
            ppt += 30f
        }

        stats!!.peakCRDuration.modifyFlat(id, ppt)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }


}