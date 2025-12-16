package second_in_command.skills.engineering

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class CoolingSystems : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+10%% 武器射速", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+10%% 实弹与能量武器备弹回复速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        stats.missileRoFMult.modifyPercent(id, 10f)
        stats.ballisticRoFMult.modifyPercent(id, 10f)
        stats.energyRoFMult.modifyPercent(id, 10f)

        stats.ballisticAmmoRegenMult.modifyPercent(id, 10f)
        stats.energyAmmoRegenMult.modifyPercent(id, 10f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {

    }

    override fun onActivation(data: SCData) {

    }

    override fun onDeactivation(data: SCData) {

    }

}