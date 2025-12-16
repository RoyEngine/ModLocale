package second_in_command.skills.tactical

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class FullThrottle : SCBaseSkillPlugin() {

    var ZERO_FLUX_MIN = 0.1f
    var ZERO_FLUX_BOOST = 20f

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("只要舰船幅能水平*不高于 10%% 就能享受 \"零幅能加速\"效果", 0f, Misc.getHighlightColor(), Misc.getHighlightColor(), )
        tooltip.addPara("+20 \"零幅能加速\" 生效时的最高航速 ", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        tooltip.addPara("*该效果可与其他同类效果叠加，两个技能叠加后效果最多达到 20%% 的激活下限。", 0f, Misc.getGrayColor(), Misc.getHighlightColor(), "20%")
        
    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        stats!!.zeroFluxMinimumFluxLevel.modifyFlat(id, ZERO_FLUX_MIN)
        stats!!.zeroFluxSpeedBoost.modifyFlat(id, ZERO_FLUX_BOOST)


    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

}