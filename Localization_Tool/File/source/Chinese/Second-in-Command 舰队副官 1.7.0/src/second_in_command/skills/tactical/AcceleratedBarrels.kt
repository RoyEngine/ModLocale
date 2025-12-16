package second_in_command.skills.tactical

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class AcceleratedBarrels : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+10%% 非导弹武器射速", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-10%% 武器产生的幅能", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        stats!!.ballisticRoFMult.modifyPercent(id, 10f)
        stats.energyRoFMult.modifyPercent(id, 10f)

        stats!!.ballisticWeaponFluxCostMod.modifyMult(id, 0.9f)
        stats!!.energyWeaponFluxCostMod.modifyMult(id, 0.9f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

}