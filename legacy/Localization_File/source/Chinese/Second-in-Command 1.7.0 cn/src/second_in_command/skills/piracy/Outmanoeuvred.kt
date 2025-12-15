package second_in_command.skills.piracy

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.skills.Sensors
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Outmanoeuvred : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+1 最大宇宙航行速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+20%% 宇宙航行机动性", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {


    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.fleetwideMaxBurnMod.modifyFlat("sc_outmaneuvered", 1f, "诡诈机动")
        data.fleet.stats.accelerationMult.modifyPercent("sc_outmaneuvered", 20f, "诡诈机动")
    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.fleetwideMaxBurnMod.modifyFlat("sc_outmaneuvered", 1f, "诡诈机动")
        data.fleet.stats.accelerationMult.modifyPercent("sc_outmaneuvered", 20f, "诡诈机动")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.fleetwideMaxBurnMod.unmodify("sc_outmaneuvered")
        data.fleet.stats.accelerationMult.unmodify("sc_outmaneuvered")
    }

}