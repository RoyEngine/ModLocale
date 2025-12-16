package second_in_command.skills.piracy

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class LowgradeDeployment : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("你所有舰船如果在战斗中被击沉，将几乎总是可在战斗后将其打捞和修复", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-30%% 战斗部署成本", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+20%% 战斗外的维修速率", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        stats!!.suppliesToRecover.modifyMult(id, 0.7f)
        stats.repairRatePercentPerDay.modifyPercent(id, 20f)

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).modifyFlat("sc_low_grade_deployment", 1.5f)

    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).modifyFlat("sc_low_grade_deployment", 1.5f)

    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).unmodify("sc_low_grade_deployment")
    }

}