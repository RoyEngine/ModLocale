package second_in_command.skills.tactical

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class RapidResponse : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("最大宇宙航行速度低于 9 的舰船，最大宇宙航行速度 +1", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+15%% 宇宙航行机动性", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        if (stats!!.maxBurnLevel.modifiedValue < 9) {
            stats!!.maxBurnLevel.modifyFlat(id,1f)
        }
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.accelerationMult.modifyPercent("sc_rapid_response", 15f, "快速反应")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.accelerationMult.unmodify("sc_rapid_response")
    }

}