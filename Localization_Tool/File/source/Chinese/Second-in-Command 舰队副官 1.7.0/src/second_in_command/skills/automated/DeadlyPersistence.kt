package second_in_command.skills.automated

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class DeadlyPersistence : SCBaseSkillPlugin() {


    var ZERO_FLUX_MIN = 0.1f
    var VENT_RATE = 20f
    var COOLDOWN_REDUCTION = 0.9f


    override fun getAffectsString(): String {
        return "所有自动化舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("只要舰船幅能水平不高于 10%%* 就能享受 \"零幅能加速\"效果", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+20%% 舰船主动排幅速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        //tooltip.addPara("-10%% on the cooldown of the ships system", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addSpacer(10f)
        tooltip.addPara("*该效果可与其他同类效果叠加，两个技能叠加后效果最多达到 20%% 的激活下限。", 0f, Misc.getGrayColor(), Misc.getHighlightColor(), "20%")
    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        if (Misc.isAutomated(stats)) {
            stats!!.zeroFluxMinimumFluxLevel.modifyFlat(id, ZERO_FLUX_MIN)
            stats.ventRateMult.modifyPercent(id, VENT_RATE)
            //stats.getSystemCooldownBonus().modifyMult(id, COOLDOWN_REDUCTION)
        }
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {
        if (Misc.isAutomated(ship)) {

        }
    }


}